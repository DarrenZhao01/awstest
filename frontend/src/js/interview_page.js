/**
 * JavaScript for the Interview page
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const startInterviewBtn = document.getElementById('start-interview-btn');
    const questionContainer = document.getElementById('question-container');
    const currentQuestionText = document.getElementById('current-question');
    const videoContainer = document.getElementById('video-container');
    const videoElement = document.getElementById('user-video');
    const audioFeedbackContainer = document.getElementById('audio-feedback-container');
    const transcriptContainer = document.getElementById('transcript-container');
    const transcriptText = document.getElementById('transcript-text');
    const recordBtn = document.getElementById('record-btn');
    const nextQuestionBtn = document.getElementById('next-question-btn');
    
    // State variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let stream;
    let currentQuestionIndex = 0;
    const questions = [
        "Tell me about yourself and your background.",
        "What experience do you have that's relevant to this position?",
        "Describe a challenging project you worked on and how you handled it.",
        "Why are you interested in this position?",
        "What are your strengths and weaknesses?"
    ]; // Placeholder questions, would be fetched from API in real app
    
    // --- Event Listeners ---
    startInterviewBtn.addEventListener('click', startInterview);
    recordBtn.addEventListener('click', toggleRecording);
    nextQuestionBtn.addEventListener('click', moveToNextQuestion);
    
    // --- Functions ---
    async function startInterview() {
        try {
            // Request camera and microphone permissions
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: true, 
                audio: true 
            });
            
            // Display the video stream
            videoElement.srcObject = stream;
            
            // Setup the MediaRecorder for audio
            const audioStream = new MediaStream(stream.getAudioTracks());
            mediaRecorder = new MediaRecorder(audioStream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = handleAudioStop;
            
            // Show the first question
            startInterviewBtn.classList.add('d-none');
            questionContainer.classList.remove('d-none');
            videoContainer.classList.remove('d-none');
            
            displayQuestion(currentQuestionIndex);
            
        } catch (error) {
            console.error('Error accessing media devices:', error);
            alert('Could not access camera or microphone. Please ensure permissions are granted.');
        }
    }
    
    function displayQuestion(index) {
        if (index < questions.length) {
            currentQuestionText.textContent = questions[index];
            recordBtn.disabled = false;
            nextQuestionBtn.disabled = true;
            transcriptContainer.classList.add('d-none');
            audioFeedbackContainer.classList.add('d-none');
        } else {
            // End of interview
            questionContainer.innerHTML = '<h2>Interview Complete!</h2><p>Thank you for completing the practice interview. Click below to see your feedback.</p>';
            videoContainer.classList.add('d-none');
            const feedbackButton = document.createElement('a');
            feedbackButton.href = 'feedback.html';
            feedbackButton.className = 'btn btn-primary btn-lg';
            feedbackButton.textContent = 'View Feedback';
            questionContainer.appendChild(feedbackButton);
        }
    }
    
    function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }
    
    function startRecording() {
        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        recordBtn.textContent = 'Stop Recording';
        recordBtn.classList.remove('btn-primary');
        recordBtn.classList.add('btn-danger');
    }
    
    function stopRecording() {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.textContent = 'Record Answer';
        recordBtn.classList.remove('btn-danger');
        recordBtn.classList.add('btn-primary');
        recordBtn.disabled = true;
    }
    
    async function handleAudioStop() {
        // Create audio blob from chunks
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        try {
            console.log('Processing audio recording...');
            
            // Simulate server processing time
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Mock transcript response
            const mockTranscript = "This is a simulated transcript of your response. In a real application, this would be generated by AWS Transcribe from your audio recording.";
            
            // Display transcript
            transcriptContainer.classList.remove('d-none');
            transcriptText.textContent = mockTranscript;
            
            // Enable next question button
            nextQuestionBtn.disabled = false;
            
            // Show audio feedback
            audioFeedbackContainer.classList.remove('d-none');
            
        } catch (error) {
            console.error('Error processing audio:', error);
            alert('There was an error processing your response. Please try again.');
            recordBtn.disabled = false;
        }
    }
    
    function moveToNextQuestion() {
        currentQuestionIndex++;
        displayQuestion(currentQuestionIndex);
    }
    
    // Clean up resources when leaving the page
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
}); 