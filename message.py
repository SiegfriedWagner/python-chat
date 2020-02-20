from dataclasses import dataclass
import pickle


class Serializable:

    @classmethod
    def from_bytes(cls, bytearr: bytes):
        obj = pickle.loads(bytearr)
        if not isinstance(obj, cls):
            raise TypeError(f"Unpickled object is not instance of {cls}")
        return obj

    def __bytes__(self):
        return pickle.dumps(self)


@dataclass
class ChatMessage(Serializable):
    sender: str
    text: str
    timestamp: float

    @classmethod
    def from_string(cls, string: str):
        print("Chat " + string)
        splited = string.split(":")
        timestamp, sender, text = splited[0], splited[1], splited[2:]
        text = "".join(text)
        return ChatMessage(timestamp=float(timestamp), sender=sender, text=text)

    def __str__(self):
        return f"{self.timestamp}:{self.sender}:{self.text}"


@dataclass
class LogMessage(Serializable):
    sender: str
    type: str
    data: str
    timestamp: float


@dataclass
class IntroductionMessage(Serializable):
    nickname: str
    name: str
    gender: str
    age: int
