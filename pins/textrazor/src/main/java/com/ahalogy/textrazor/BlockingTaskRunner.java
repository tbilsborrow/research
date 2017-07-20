package com.ahalogy.textrazor;

import java.util.concurrent.Callable;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorCompletionService;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

/**
 * Helper to run tasks in parallel with desired amount of concurrency.
 * <p>
 * Currently only has the one submit method, and this method *will* block
 * if this runner is "full" (meaning if this runner has concurrency N and
 * there are already N tasks running, a call to submit will block until one
 * of those running tasks (and its callback) is done).
 * <p>
 * You should absolutely call the close() method when you are through submitting
 * tasks. This will block until all running tasks are done.
 *
 * @param <T> This should be the type of the result returned by the tasks.
 */
class BlockingTaskRunner<T> implements AutoCloseable {
    private final int concurrency;

    private final ExecutorService executor;
    private final ExecutorCompletionService<T> service;

    private int activeTasks = 0;

    BlockingTaskRunner(int concurrency) {
        this.concurrency = concurrency;
        executor = Executors.newFixedThreadPool(concurrency);
        service = new ExecutorCompletionService<>(executor);
    }

    // ** POTENTIALLY BLOCKING **
    synchronized Future<T> submit(Callable<T> task) {
        if (activeTasks >= concurrency) {
            // block until an existing task is done
            try {
                service.take().get();
            } catch (InterruptedException | ExecutionException e) {
                throw new CompletionException(e);
            }
            activeTasks -= 1;
        }
        activeTasks += 1;
        return service.submit(task);
    }

    // ** POTENTIALLY BLOCKING **
    @Override
    synchronized public void close() {
        try {
            while (activeTasks > 0) {
                // block until all tasks done
                service.take().get();
                activeTasks -= 1;
            }

            executor.shutdown();
            executor.awaitTermination(12, TimeUnit.HOURS);
        } catch (InterruptedException | ExecutionException e) {
            throw new CompletionException(e);
        }
    }
}
