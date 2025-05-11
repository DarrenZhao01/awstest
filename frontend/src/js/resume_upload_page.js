/**
 * JavaScript for the Resume Upload page
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const resumeDropArea = document.getElementById('resume-drop-area');
    const resumeInput = document.getElementById('resume-input');
    const resumeBrowseBtn = document.getElementById('resume-browse-btn');
    const resumeProgressContainer = document.getElementById('resume-progress-container');
    const resumeProgress = document.getElementById('resume-progress');
    const resumeFileName = document.getElementById('resume-file-name');
    const resumeStatusMessage = document.getElementById('resume-status-message');
    
    const jdDropArea = document.getElementById('jd-drop-area');
    const jdInput = document.getElementById('jd-input');
    const jdBrowseBtn = document.getElementById('jd-browse-btn');
    const jdProgressContainer = document.getElementById('jd-progress-container');
    const jdProgress = document.getElementById('jd-progress');
    const jdFileName = document.getElementById('jd-file-name');
    const jdStatusMessage = document.getElementById('jd-status-message');
    
    const startAnalysisBtn = document.getElementById('start-analysis-btn');
    const analysisPrompt = document.getElementById('analysis-prompt');
    const startAnalysisBtnLink = document.getElementById('start-analysis-btn-link');

    // State variables
    let resumeFileSuccessfullyUploaded = false;
    let jdFileSuccessfullyUploaded = false;

    // --- Event Listeners ---
    resumeBrowseBtn.addEventListener('click', () => resumeInput.click());
    jdBrowseBtn.addEventListener('click', () => jdInput.click());
    
    resumeInput.addEventListener('change', (e) => handleFileSelect(e.target, 'resume'));
    jdInput.addEventListener('change', (e) => handleFileSelect(e.target, 'jd'));
    
    setupDragAndDrop(resumeDropArea, resumeInput, 'resume');
    setupDragAndDrop(jdDropArea, jdInput, 'jd');

    startAnalysisBtn.addEventListener('click', () => {
        if (resumeFileSuccessfullyUploaded && jdFileSuccessfullyUploaded) {
            window.location.href = 'interview.html';
        } else {
            alert('Please ensure both resume and job description are successfully uploaded.');
        }
    });

    // --- Core Functions ---
    function handleFileSelect(inputElement, fileType) {
        if (inputElement.files.length > 0) {
            const file = inputElement.files[0];
            const { fileNameElement, progressContainer, progressBar, statusMessageElement } = getDOMElementsForType(fileType);
            
            fileNameElement.textContent = file.name;
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            progressBar.classList.remove('bg-success', 'bg-danger');
            statusMessageElement.textContent = 'Uploading...';
            statusMessageElement.className = 'file-status-message'; // Reset classes

            uploadFile(file, fileType);
        }
    }

    async function uploadFile(file, fileType) {
        const { progressBar, statusMessageElement } = getDOMElementsForType(fileType);
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('fileType', fileType);
        
        try {
            // For local testing, simulate successful upload
            console.log(`Uploading ${fileType} file: ${file.name}`);
            
            // Simulate server processing time
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Simulate successful response
            const mockResponse = {
                message: `File '${file.name}' uploaded successfully as ${fileType} to S3.`,
                filename: file.name,
                s3_key: `${fileType === 'resume' ? 'resumes' : 'job_descriptions'}/${file.name}`
            };
            
            progressBar.style.width = '100%';
            progressBar.classList.add('bg-success');
            statusMessageElement.textContent = 'Upload successful!';
            statusMessageElement.classList.add('text-success');
            
            // Update state
            if (fileType === 'resume') {
                resumeFileSuccessfullyUploaded = true;
            } else {
                jdFileSuccessfullyUploaded = true;
            }
            
            // Check if both files are uploaded
            if (resumeFileSuccessfullyUploaded && jdFileSuccessfullyUploaded) {
                startAnalysisBtn.disabled = false;
                if (startAnalysisBtnLink) {
                    startAnalysisBtnLink.classList.remove('d-none');
                    startAnalysisBtn.classList.add('d-none');
                }
                analysisPrompt.textContent = 'Both files uploaded successfully. Ready to proceed!';
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            progressBar.style.width = '100%';
            progressBar.classList.add('bg-danger');
            statusMessageElement.textContent = 'Upload failed. Please try again.';
            statusMessageElement.classList.add('text-danger');
        }
    }

    function setupDragAndDrop(dropArea, inputElement, fileType) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add('highlight');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove('highlight');
            }, false);
        });
        
        dropArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                inputElement.files = files;
                handleFileSelect(inputElement, fileType);
            }
        }, false);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function getDOMElementsForType(fileType) {
        if (fileType === 'resume') {
            return {
                fileNameElement: resumeFileName,
                progressContainer: resumeProgressContainer,
                progressBar: resumeProgress,
                statusMessageElement: resumeStatusMessage
            };
        } else {
            return {
                fileNameElement: jdFileName,
                progressContainer: jdProgressContainer,
                progressBar: jdProgress,
                statusMessageElement: jdStatusMessage
            };
        }
    }
}); 