
class Task():
    def __init__(self, name: str, is_processing: bool, state: str, transcript: str, processed_filename: str, progress=0):
        self.name = name
        self.is_processing = is_processing
        self.state = state #ready, processing, evalluation, finished
        self.transcript = transcript
        self.processed_filename = processed_filename
        self.progress = progress
        pass
    
    def toJSON(self):
        return {
            "task_name": self.name, #action items, summary
            "processing": self.is_processing,
            "state" : self.state, #ready, processing, evalluation, finished
            "transcript": self.transcript,  
            "processed_filename": self.processed_filename, #transcript filename,
            "progress": self.progress #transcript filename
        }