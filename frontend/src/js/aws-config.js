/**
 * AWS Amplify Configuration
 * This file contains the configuration for AWS Amplify services.
 * You need to replace the placeholder values with your actual AWS resource values
 * after running 'amplify init', 'amplify add auth', etc.
 */

// Initialize Amplify
function initializeAmplify() {
    // Replace these values with the actual values from your Amplify CLI configuration
    // These values will be available after you run the relevant Amplify CLI commands
    const awsConfig = {
        Auth: {
            // Amazon Cognito Region
            region: 'us-west-2',
            
            // Amazon Cognito User Pool ID
            userPoolId: 'REPLACE_WITH_YOUR_USER_POOL_ID',
            
            // Amazon Cognito Web Client ID (26-char alphanumeric string)
            userPoolWebClientId: 'REPLACE_WITH_YOUR_CLIENT_ID',
            
            // Enforces user authentication prior to accessing AWS resources
            mandatorySignIn: true,
        },
        Storage: {
            // S3 Configuration
            AWSS3: {
                bucket: 'REPLACE_WITH_YOUR_S3_BUCKET_NAME', // e.g. 'awscloudhacks2025-storage1234-dev'
                region: 'us-west-2',
            }
        },
        API: {
            endpoints: [
                {
                    name: "resumeUploadApi",
                    endpoint: "REPLACE_WITH_YOUR_API_GATEWAY_URL/upload-file", // Replace with actual API Gateway URL
                    region: "us-west-2"
                },
                {
                    name: "audioUploadApi",
                    endpoint: "REPLACE_WITH_YOUR_API_GATEWAY_URL/upload-audio", // Replace with actual API Gateway URL
                    region: "us-west-2"
                }
            ]
        }
    };

    // Initialize Amplify with the configuration
    AWS.Amplify.configure(awsConfig);
    
    console.log('AWS Amplify initialized successfully');
}

// Export the initialization function
window.initializeAmplify = initializeAmplify;

// Call the function when the script loads
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeAmplify();
    } catch (error) {
        console.error('Error initializing AWS Amplify:', error);
    }
}); 