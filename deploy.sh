#!/bin/bash
set -e

SERVICE_NAME="ai-resume-match"
IMAGE_NAME="${SERVICE_NAME}-app"
PORT="5000"

# --- 1. Validate environment variable ---
if [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ Please export your OpenAI API key before running this script:"
  echo "   export OPENAI_API_KEY=sk-xxxxxx"
  exit 1
fi

echo "🔑 Using OpenAI API Key from environment."

# --- 2. Build Docker image for amd64 (Lightsail default platform) ---
echo "🚀 Building Docker image for $SERVICE_NAME..."
docker buildx build --platform linux/amd64 -t $IMAGE_NAME . --load

# --- 3. Push image to Lightsail private registry ---
echo "📦 Pushing image to AWS Lightsail..."
PUSH_OUTPUT=$(aws lightsail push-container-image \
  --service-name $SERVICE_NAME \
  --label $SERVICE_NAME \
  --image $IMAGE_NAME)

if [ $? -ne 0 ]; then
  echo "❌ Failed to push image to Lightsail."
  exit 1
fi

# --- 4. Get latest registered image reference ---
echo "🔍 Fetching latest image version from Lightsail registry..."
LATEST_IMAGE=$(aws lightsail get-container-images \
  --service-name $SERVICE_NAME \
  --query 'containerImages[-1].image' \
  --output text)

if [ -z "$LATEST_IMAGE" ] || [ "$LATEST_IMAGE" = "None" ]; then
  echo "❌ Could not determine latest image version."
  exit 1
fi

echo "✅ Latest image registered: $LATEST_IMAGE"

# --- 5. Create YAML template with env placeholder ---
echo "📝 Creating deployment configuration..."
cat > lightsail.yaml <<EOF
serviceName: $SERVICE_NAME
containers:
  $SERVICE_NAME:
    image: $LATEST_IMAGE
    environment:
      OPENAI_API_KEY: "\${OPENAI_API_KEY}"
    ports:
      "$PORT": HTTP
publicEndpoint:
  containerName: $SERVICE_NAME
  containerPort: $PORT
EOF

# --- 6. Inject env vars securely using envsubst ---
echo "🔐 Injecting environment variables securely..."
envsubst < lightsail.yaml > lightsail.resolved.yaml

# --- 7. Deploy to Lightsail ---
echo "🚢 Deploying to AWS Lightsail..."
aws lightsail create-container-service-deployment \
  --service-name $SERVICE_NAME \
  --cli-input-yaml file://lightsail.resolved.yaml

# --- 8. Monitor deployment status ---
echo "⏱️ Monitoring deployment progress..."
while true; do
  STATUS=$(aws lightsail get-container-services \
    --service-name $SERVICE_NAME \
    --query "containerServices[0].state" \
    --output text)
  echo "$(date '+%H:%M:%S') → $STATUS"
  if [ "$STATUS" = "RUNNING" ]; then
    echo "✅ Deployment successful! Service is RUNNING."
    URL=$(aws lightsail get-container-services \
      --service-name $SERVICE_NAME \
      --query "containerServices[0].url" \
      --output text)
    echo "🌐 Visit your app at: $URL"
    break
  elif [[ "$STATUS" =~ (FAILED|CANCELED) ]]; then
    echo "❌ Deployment failed or canceled."
    exit 1
  fi
  sleep 5
done

# --- 9. Cleanup ---
rm -f lightsail.resolved.yaml
echo "🧹 Cleaned up temporary files."
echo "🎉 Done!"
