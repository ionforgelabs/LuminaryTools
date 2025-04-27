using System.Security.Cryptography;
using System.Text;
using LuminaryEngine.Extras;
using LunimaryEngine.Engine.Configuration;

namespace LogDecryptor;

class Program
{
    private static readonly string _logFilePath = "logs.lme"; // Path to the finalized encrypted log file
    private static readonly string _outputFilePath = "decrypted.log"; // Path to the output decrypted log file
    private static string _encryptionPassword; // Password used for encryption

    static void Main(string[] args)
    {
        _encryptionPassword = ConfigManager.GetConfigValue("EncryptionKey", "./appsettings.json");

        Console.WriteLine("Log Decrypt Utility");
        Console.WriteLine("======================\n");

        // Parse command-line arguments for ignored log types
        var ignoredLogTypes = args
            .Where(arg => arg.StartsWith("--ignore=", StringComparison.OrdinalIgnoreCase))
            .Select(arg => arg.Substring("--ignore=".Length).ToUpper())
            .ToHashSet();

        if (ignoredLogTypes.Any())
        {
            Console.WriteLine("Ignoring log types: " + string.Join(", ", ignoredLogTypes));
        }

        try
        {
            if (!File.Exists(_logFilePath))
            {
                Console.WriteLine("No finalized log file found.");
                return;
            }

            // Read the encrypted log content
            string encryptedLog = File.ReadAllText(_logFilePath);

            // Decrypt the log
            string decryptedLog = EncryptionUtils.Decrypt(encryptedLog, _encryptionPassword);

            // Split the concatenated log entries using the delimiter
            string[] logEntries = decryptedLog.Split('|');

            // Filter out ignored log types and write the remaining logs to the output file
            using (StreamWriter writer = new StreamWriter(_outputFilePath))
            {
                foreach (string logEntry in logEntries)
                {
                    // Each log entry is expected to follow the format: "LOGLEVEL::Timestamp::Message"
                    string logLevel = logEntry.Split("::")[0].ToUpper();

                    if (!ignoredLogTypes.Contains(logLevel))
                    {
                        writer.WriteLine(logEntry);
                    }
                }
            }

            Console.WriteLine($"Decrypted logs have been written to: {_outputFilePath}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error reading logs: {ex.Message}");
        }
    }
}