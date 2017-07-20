package com.ahalogy.textrazor;

import com.textrazor.AnalysisException;
import com.textrazor.TextRazor;
import com.textrazor.annotations.AnalyzedText;
import com.textrazor.annotations.Response;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Timing/concurrency test. Parameters are hard-coded.
 */
public class TextRazorTest {
    private static final String TEXTRAZOR_API_KEY = "078fbfb764d9d56ce09815299032d845fd776bf1b7b1ec6afd2bc838";

    // how many threads to use
    private static final int TEXTRAZOR_CONCURRENCY = 15;

    // one pin description per line
    private static final String INPUT_FILENAME = "pin-descriptions.txt";
    // number of lines from the file to skip
    private static final int OFFSET = 2000;
    // total number of pins to send to TextRazor
    private static final int LIMIT = 1500;

    public static void main(String[] args) throws IOException, AnalysisException, ExecutionException, InterruptedException {
        final TextRazor client = new TextRazor(TEXTRAZOR_API_KEY);
        client.addExtractor("entities");
        client.setLanguageOverride("eng");

        int counter = 0;
        final AtomicLong totalDuration = new AtomicLong(0);
        final long start = System.currentTimeMillis();

        try (
                final BufferedReader reader = new BufferedReader(new FileReader(INPUT_FILENAME));
                final BlockingTaskRunner<Response> taskRunner = new BlockingTaskRunner<>(TEXTRAZOR_CONCURRENCY)
        ) {
            String line;
            while (((line = reader.readLine()) != null) && (counter < OFFSET + LIMIT)) {
                counter += 1;
                final String text = line;
                if (counter >= OFFSET) {
                    final int c = counter;
                    taskRunner.submit(() -> {
                        try {
                            final long taskStart = System.currentTimeMillis();
                            final AnalyzedText response = client.analyze(text);
                            final long taskDuration = (System.currentTimeMillis() - taskStart);
                            totalDuration.addAndGet(taskDuration);
                            return response.getResponse();
                        } catch (Throwable t) {
                            System.out.println(String.format(">>>>>>>>>>> [%d] %s", c, text));
                            t.printStackTrace();
                            return null;
                        }
                    });
                }
            }
        }
        final long duration = (System.currentTimeMillis() - start);

        counter -= OFFSET;
        System.out.println(String.format("count: %d", counter));
        System.out.println(String.format("overall duration: %.3f", duration / 1000.0));
        System.out.println(String.format("overall rate: %.3f per second", (counter / (duration / 1000.0))));
        System.out.println(String.format("total time spent making requests: %.3f", totalDuration.get() / 1000.0));
        System.out.println(String.format("avg time per request: %.3f", totalDuration.get() / counter / 1000.0));
    }
}
