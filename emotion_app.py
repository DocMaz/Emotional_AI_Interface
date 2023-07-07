import sys
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QFont
from textblob import TextBlob

class SpeechRecognitionThread(QThread):
    sentiment_detected = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.recognizer = sr.Recognizer()
        self.running = True

    def run(self):
        while self.running:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)

            try:
                # Convert the speech to text
                speech_text = self.recognizer.recognize_google(audio)

                # Determine the sentiment
                sentiment = TextBlob(speech_text).sentiment.polarity

                # Emit a signal with the sentiment
                self.sentiment_detected.emit(str(sentiment))

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def stop(self):
        self.running = False

class EmotionApp(QWidget):
    def __init__(self):
        super().__init__()

        # Create a vertical layout
        self.layout = QVBoxLayout()

        # Create a label for the emoticon
        self.emoticon_label = QLabel(":|")
        self.emoticon_label.setAlignment(Qt.AlignCenter)
        self.emoticon_label.setFont(QFont("Arial", 400))

        # Set the color of the label to blue
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor("blue"))
        self.emoticon_label.setPalette(palette)

        # Add the label to the layout
        self.layout.addWidget(self.emoticon_label, 0, Qt.AlignCenter)

        # Create a button to stop the application
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)

        # Add the button to the layout
        self.layout.addWidget(self.stop_button)

        # Set the layout on the application's window
        self.setLayout(self.layout)

        # Set the background color to black
        palette.setColor(QPalette.Window, QColor("black"))
        self.setPalette(palette)

        # Initialize the speech recognition thread
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.sentiment_detected.connect(self.update_labels)
        self.speech_thread.start()

    def update_labels(self, sentiment):
        # Convert the sentiment to a float
        sentiment = float(sentiment)

        # Update the emoticon based on the sentiment
        if sentiment > 0.1:
            self.emoticon_label.setText(":)")
        elif sentiment < -0.1:
            self.emoticon_label.setText(":(")
        else:
            self.emoticon_label.setText(":|")

    def stop(self):
        # Stop the speech recognition thread
        self.speech_thread.stop()

        # Close the application
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EmotionApp()
    window.showFullScreen()  # Make the window full screen

    sys.exit(app.exec_())
