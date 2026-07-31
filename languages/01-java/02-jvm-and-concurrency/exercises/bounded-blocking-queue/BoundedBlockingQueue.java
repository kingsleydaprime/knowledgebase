/**
 * A thread-safe queue with a fixed capacity.
 *
 * Requirements:
 *  - put(item) blocks while the queue is full, until a take() frees a slot.
 *  - take() blocks while the queue is empty, until a put() adds an item.
 *  - Multiple producer and consumer threads may call put()/take() concurrently
 *    without losing, duplicating, or corrupting items.
 *  - take() returns items in the same order they were put() (FIFO).
 *
 * Do not use java.util.concurrent.BlockingQueue or any of its implementations
 * (ArrayBlockingQueue, LinkedBlockingQueue, etc.) — the point is to build the
 * primitive yourself using wait()/notifyAll() or a Lock + Condition.
 *
 * Run BoundedBlockingQueueTest.java against this once implemented — see
 * ../README.md for how to compile and run it.
 */
public class BoundedBlockingQueue<T> {

    public BoundedBlockingQueue(int capacity) {
        throw new UnsupportedOperationException("implement me");
    }

    public void put(T item) throws InterruptedException {
        throw new UnsupportedOperationException("implement me");
    }

    public T take() throws InterruptedException {
        throw new UnsupportedOperationException("implement me");
    }

    public int size() {
        throw new UnsupportedOperationException("implement me");
    }
}
