class PushMatrix:
    queue = list()

    def __init__(self, transform, kwargs):
        self.transform = transform
        self.kwargs = kwargs
        self._is_finished = False
        PushMatrix.queue.append(self)

    def is_finished(self):
        return self._is_finished

    def finished(self):
        self._is_finished = True

    @staticmethod
    def exec():
        if PushMatrix.queue:
            q = PushMatrix.queue[0]
            if q.is_finished():
                q.transform(**q.kwargs)
                PushMatrix.queue.pop(0)
                PushMatrix.exec()
