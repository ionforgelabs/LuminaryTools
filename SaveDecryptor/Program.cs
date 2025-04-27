using System.Text.Json;
using LuminaryEngine.Extras;
using LunimaryEngine.Engine.Configuration;

namespace SaveDecryptor;

class Program
{
    public static void Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: SaveDecryptor <saveFilePath> [outputFolder]");
            return;
        }

        string filePath = args[0];
        string outputFolder = args.Length > 1 ? args[1] : "DecryptedSaves";

        SaveDecryptor.DecryptSaveFile(filePath, outputFolder);
    }
}

/// <summary>
/// A utility to decrypt and save the contents of an encrypted save file.
/// </summary>
public static class SaveDecryptor
{
    /// <summary>
    /// Decrypts an encrypted save file and writes the decrypted JSON data to an output folder.
    /// </summary>
    /// <param name="filePath">The path to the encrypted save file.</param>
    /// <param name="outputFolder">The folder where the decrypted JSON will be saved.</param>
    public static void DecryptSaveFile(string filePath, string outputFolder = "DecryptedSaves")
    {
        if (!File.Exists(filePath))
        {
            Console.WriteLine($"Error: Save file not found at '{filePath}'");
            return;
        }

        try
        {
            // Fetch the encryption key from the configuration file
            string password = ConfigManager.GetConfigValue("EncryptionKey", "./appsettings.json");
            if (string.IsNullOrEmpty(password))
            {
                Console.WriteLine("Error: Encryption key not found in configuration.");
                return;
            }

            // Read the encrypted data from the file
            string encryptedData = File.ReadAllText(filePath);

            // Decrypt the data using EncryptionUtils
            string decryptedData = EncryptionUtils.Decrypt(encryptedData, password);

            // Ensure the output folder exists
            if (!Directory.Exists(outputFolder))
            {
                Directory.CreateDirectory(outputFolder);
            }

            // Generate the output file path
            string outputFileName = Path.GetFileNameWithoutExtension(filePath) + "_decrypted.json";
            string outputFilePath = Path.Combine(outputFolder, outputFileName);

            // Write the decrypted data to the output file in indented JSON format
            var jsonOptions = new JsonSerializerOptions { WriteIndented = true };
            var formattedJson =
                JsonSerializer.Serialize(JsonSerializer.Deserialize<object>(decryptedData), jsonOptions);
            File.WriteAllText(outputFilePath, formattedJson);

            Console.WriteLine($"Decrypted save file written to: {outputFilePath}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: Failed to decrypt the save file. Details: {ex.Message}");
        }
    }
}