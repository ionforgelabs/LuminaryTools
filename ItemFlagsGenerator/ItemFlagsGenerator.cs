using LuminaryEngine.Engine.Gameplay.Items;

namespace ItemFlagsGenerator;

class ItemFlagsGenerator
{
    static void Main(string[] args)
    {
        Console.WriteLine("Welcome to the ItemFlags Generator!");
        Console.WriteLine("Available Flags:");
        foreach (var flag in Enum.GetValues(typeof(ItemFlags)))
        {
            Console.WriteLine($"- {flag}");
        }

        Console.WriteLine("\nEnter the flags you want to set, separated by commas (e.g., Equippable, Rare, Stackable):");
        string userInput = Console.ReadLine();

        if (string.IsNullOrWhiteSpace(userInput))
        {
            Console.WriteLine("No input provided. Defaulting to None.");
            Console.WriteLine($"Generated Flags: {ItemFlags.None}");
            return;
        }

        string[] inputs = userInput.Split(',', StringSplitOptions.RemoveEmptyEntries);
        ItemFlags resultFlags = ItemFlags.None;

        foreach (var input in inputs)
        {
            if (Enum.TryParse(input.Trim(), true, out ItemFlags flag))
            {
                resultFlags |= flag;
            }
            else
            {
                Console.WriteLine($"Warning: '{input}' is not a valid flag and will be ignored.");
            }
        }

        Console.WriteLine($"\nGenerated Flags: {resultFlags}");
        Console.WriteLine($"Numeric Value: {(int)resultFlags}");
    }
}