/**
 * Main JavaScript file for AI Interview Prep application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AWS configuration when needed
    function initializeAWS() {
        // This function would normally configure AWS Amplify
        // Example configuration (would be populated with actual values in production)
        /*
        AWS.config.region = 'us-west-2';
        AWS.config.credentials = new AWS.CognitoIdentityCredentials({
            IdentityPoolId: 'us-west-2:xxx-xxx-xxx-xxx',
        });

        Amplify.configure({
            Auth: {
                identityPoolId: 'us-west-2:xxx-xxx-xxx-xxx',
                region: 'us-west-2',
            },
            Storage: {
                AWSS3: {
                    bucket: 'ai-interview-prep-uploads',
                    region: 'us-west-2',
                }
            },
            API: {
                endpoints: [
                    {
                        name: "InterviewAPI",
                        endpoint: "https://api.example.com/interview"
                    }
                ]
            }
        });
        */
        console.log('AWS services would be initialized here in production');
    }

    // Handle copy buttons (used in various places)
    const copyButtons = document.querySelectorAll('.btn-outline-secondary');
    if (copyButtons.length > 0) {
        copyButtons.forEach(button => {
            if (button.previousElementSibling && button.previousElementSibling.tagName === 'INPUT') {
                button.addEventListener('click', function() {
                    const inputElement = this.previousElementSibling;
                    inputElement.select();
                    document.execCommand('copy');
                    
                    // Change button text temporarily
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                });
            }
        });
    }

    // Display notification toast
    function showToast(message, type = 'success') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create the toast element
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        // Toast content
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add to container
        toastContainer.appendChild(toastEl);
        
        // Initialize and show the toast
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove after it's hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }

    // Expose functions to global scope
    window.aiInterviewApp = {
        initializeAWS,
        showToast
    };
}); 