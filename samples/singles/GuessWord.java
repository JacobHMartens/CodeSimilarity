import java.io.*;

class GuessWord
{
    public static int ReadWordsFromFile(String[] words)
    {
        try
        {
            FileReader fr = new FileReader("words_input.txt");
            BufferedReader br = new BufferedReader(fr);
            int count = 0;
            for (int i = 0; i < 100; i++)
            {
                String s = br.readLine();
                if (s == null)
                    break;
                words[count++] = s;
            }
            fr.close();
            return count;
        }
        catch (FileNotFoundException e)
        {
            System.out.println(e.getMessage());
            return -1;
        }
        catch (IOException err)
        {
            System.out.println(err.getStackTrace());
            return -1;
        }
    }

    static public String ReadString()
    {
        try
        {
            String inpString = "";
            InputStreamReader input = new InputStreamReader(System.in);
            BufferedReader reader = new BufferedReader(input);
            return reader.readLine();
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return "";
    }

    public static void main(String[] args)
    {
        System.out.println("Welcome to Guess a Word\n");
        String[] words = new String[100];
        int count = ReadWordsFromFile(words);
        
        if (count < 0)
        {
            System.out.println("No words found in the file");
            return;
        }

        if (words == null)
            return; // Exception message was already shown

        int x = (int) (Math.random() * 100);
        int guessX = (x % count);
        String secretWord = words[guessX];
        int numChars = secretWord.length();
        System.out.print("Your secret word is: ");
        for (int i = 0; i < numChars; i++)
            System.out.print("*");
        System.out.println();
        boolean bGuessedCorrectly = false;
        System.out.println("Guess now  (To stop the program, enter #) : ");

        while (true)
        {
            String choice = ReadString();
            if (choice.startsWith("#"))
                break;
            if (choice.compareTo(secretWord) == 0)
            {
                bGuessedCorrectly = true;
                break;
            }

            for (int i = 0; i < numChars; i++)
            {
                if (i < secretWord.length() &&
                        i < choice.length())
                {
                    if (secretWord.charAt(i) == choice.charAt(i))
                        System.out.print(choice.charAt(i));
                    else
                        System.out.print("*");
                }
                else
                    System.out.print("*");
            }
            System.out.println();
        }

        if (bGuessedCorrectly == false)
            System.out.println("Unfortunately you did not guess it correctly. The secret word is: " + secretWord);
        else
            System.out.println("Congrats! You have guessed it correctly");
    }
}