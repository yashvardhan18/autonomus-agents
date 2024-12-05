
import unittest
from inbox_outbox import MessageQueue

class TestMessageQueue(unittest.TestCase):
    def setUp(self):
        self.queue = MessageQueue()

    def test_add_and_get_message(self):
        message = {"type": "random_message", "content": "hello world"}
        self.queue.add_message(message)

      
        self.assertEqual(self.queue.get_message(), message)

        
        self.assertIsNone(self.queue.get_message())
