import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;

public class TTSClient {
    public static void main(String[] args) {
        String apiUrl = "http://localhost:5000/tts";
        String outputDir = "./gen_audio";
        String outputFileName = "output.wav";

        // Create the output directory if it doesn't exist
        File dir = new File(outputDir);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        try {
            // Set up the JSON payload
            String payload = "{"
                    + "\"username\": \"default\","
                    + "\"text\": \"Good morning team.  Having fun testing the A P I .    \""
                    + "}";

            // Open connection to the API
            URL url = new URL(apiUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            // Send the payload
            try (OutputStream os = connection.getOutputStream()) {
                os.write(payload.getBytes());
                os.flush();
            }

            // Check the response
            int responseCode = connection.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                // Save the response (audio file) to the specified directory
                try (InputStream inputStream = connection.getInputStream();
                     FileOutputStream fileOutputStream = new FileOutputStream(Paths.get(outputDir, outputFileName).toString())) {

                    byte[] buffer = new byte[4096];
                    int bytesRead;
                    while ((bytesRead = inputStream.read(buffer)) != -1) {
                        fileOutputStream.write(buffer, 0, bytesRead);
                    }
                }
                System.out.println("Audio file saved successfully to " + outputDir + "/" + outputFileName);
            } else {
                // Print error response
                try (InputStream errorStream = connection.getErrorStream();
                     BufferedReader reader = new BufferedReader(new InputStreamReader(errorStream))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.err.println(line);
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
