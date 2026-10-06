import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class AddVoiceClient {
    public static void main(String[] args) {
        String apiUrl = "http://localhost:5000/add_voice";
        String boundary = "----Boundary";

        String username = "homer";
        String refAudioFile = "beer22.wav";
        String refText = "The other day I was so desperate for a beer I snuck into the football stadium and ate the dirt under the bleachers.";

        // Check if the reference audio file exists
        File audioFile = new File(refAudioFile);
        if (!audioFile.exists()) {
            System.err.println("Error: Reference audio file not found: " + refAudioFile);
            return;
        }

        try {
            // Set up the HTTP connection
            URL url = new URL(apiUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setDoOutput(true);
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);

            // Prepare the form-data body
            try (DataOutputStream out = new DataOutputStream(connection.getOutputStream())) {
                // Add username field
                out.writeBytes("--" + boundary + "\r\n");
                out.writeBytes("Content-Disposition: form-data; name=\"username\"\r\n\r\n");
                out.writeBytes(username + "\r\n");

                // Add text field
                out.writeBytes("--" + boundary + "\r\n");
                out.writeBytes("Content-Disposition: form-data; name=\"text\"\r\n\r\n");
                out.writeBytes(refText + "\r\n");

                // Add file field
                out.writeBytes("--" + boundary + "\r\n");
                out.writeBytes("Content-Disposition: form-data; name=\"file\"; filename=\"" + audioFile.getName() + "\"\r\n");
                out.writeBytes("Content-Type: audio/wav\r\n\r\n");
                try (FileInputStream fileInput = new FileInputStream(audioFile)) {
                    byte[] buffer = new byte[4096];
                    int bytesRead;
                    while ((bytesRead = fileInput.read(buffer)) != -1) {
                        out.write(buffer, 0, bytesRead);
                    }
                }
                out.writeBytes("\r\n");
                out.writeBytes("--" + boundary + "--\r\n");
            }

            // Get the response
            int responseCode = connection.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                System.out.println("Voice added successfully for user: " + username);
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println(line);
                    }
                }
            } else {
                System.err.println("Error: Received response code " + responseCode);
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()))) {
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
