const extract = document.getElementById("extract_btn")
const start_btn = document.getElementById("start-btn")
const content = document.querySelector('#content');

const submit_btn = document.getElementById("submit-btn")
const uploadForm = document.getElementById("upload-form")
const msg = document.getElementById("msg")
const sentences = document.getElementById("sentences")
const input = document.getElementById("input-file")

console.log(submit_btn);

submit_btn.addEventListener('click', ()=>{
    var file = input.files[0]
    console.log(file);
    if (file) {
        var url = URL.createObjectURL(file);
        var mediaElement = document.createElement(file.type.startsWith('audio') ? 'audio' : 'video');
        mediaElement.src = url;

        mediaElement.addEventListener('loadedmetadata', function () {
            var duration = Math.round(mediaElement.duration);
            console.log('File duration:', duration, 'seconds');
            durationMinute = (duration/60);
            console.log(durationMinute);
            if (duration > 60){
                $('#msg').text(`Please Wait ${durationMinute} minute While Extracting Main Points`)
                $('#msg').show()
            }
            else{
                $('#msg').text(`Please Wait ${duration} seconds While Extracting Main Points`)
                $('#msg').show()
            }
        });
    }
})

sentences.addEventListener('change', ()=>{
    msg.style.add("display: none;")
})

window.addEventListener('load', ()=>{
    
})


submit_btn.addEventListener('click', ()=>{
    console.log('button click')
    $('#msg').text("Please Wait Processing To Extract Main Points")
    $('#msg').show()
    
})


function speak(sentence) {
    const text_speak = new SpeechSynthesisUtterance(sentence);

    text_speak.rate = 1;
    text_speak.pitch = 1;

    window.speechSynthesis.speak(text_speak);
}



function startListening() {
    console.log("function call");
    
    // Check permission status
    if (navigator.permissions && navigator.permissions.query) {
        navigator.permissions.query({ name: 'microphone' }).then(function(permissionStatus) {
            if (permissionStatus.state === 'granted') {
                // Microphone access is already granted
                startRecognition();
            } else {
                requestMicrophonePermission();
            }
        });
    }
}
let recognition = null; // Declare recognition as a global variable

function startRecognition() {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-IN'
    
    recognition.continuous = true;
    let interimTranscript = '';
    let finalTranscript = '';

    recognition.onresult = function(event) {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            finalTranscript += transcript
        }
    }

    recognition.onend = function() {
        // When the recognition ends (e.g., when you stop it), send the entire transcript to the server
        $.ajax({
            url: "/from_meetings/",
            method: "POST",
            data: {
                query: finalTranscript,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                console.log(data);
                speak(data);
                var dataList = $('#data-list');
                data.forEach(function(item) {
                    var listItem = $('<li>').text(item);
                    dataList.append(listItem);
                    
                })
            }
        });

        // Reset the transcript variables for the next session
        
        finalTranscript = '';
    }

    recognition.start();
}

function stopRecognition() {
    if (recognition) {
        recognition.stop();
    }
}

function requestMicrophonePermission() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
            startRecognition();
        })
        .catch(function (error) {
            console.error('Error accessing microphone:', error);
            alert("Please grant microphone access to use voice input.");
        });
}

start_btn.addEventListener('click', ()=>{
    console.log("button click")
    start_btn.textContent = "Listening..."
    startListening();
})

extract.addEventListener('click', ()=>{
    console.log("button click")
    start_btn.textContent = "Start Listening"
    stopRecognition();
})

async function handleFileSelect(event) {
    const file = event.target.files[0];

    if (file) {
        try {
            const audioBuffer = await convertAudioToBuffer(file);
            const text = await convertAudioToText(audioBuffer);

            document.getElementById('transcription').textContent = text;
        } catch (error) {
            console.error('Error:', error.message);
        }
    }
}

function convertAudioToBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (event) => {
            const arrayBuffer = event.target.result;
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            audioContext.decodeAudioData(arrayBuffer, resolve, reject);
        };

        reader.readAsArrayBuffer(file);
    });
}

function convertAudioToText(audioBuffer) {
    return new Promise((resolve, reject) => {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const audioSource = audioContext.createBufferSource();
        audioSource.buffer = audioBuffer;

        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

        recognition.lang = 'en-US';
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            resolve(transcript);
        };

        recognition.onerror = (event) => {
            reject(new Error(`Speech recognition error: ${event.error}`));
        };

        audioSource.connect(audioContext.destination);
        audioSource.start();

        recognition.start();
    });
}