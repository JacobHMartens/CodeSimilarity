import javalang



def minify_java(src: str) -> str:
    tokens = list(javalang.tokenizer.tokenize(src))
    # print(list(map(lambda t: f"{t.__class__.__name__} {t.value}", tokens)))
    
    return javalang.tokenizer.reformat_tokens(tokens)
    
    
if __name__ == "__main__":
    # Example usage
    src_code = """
    public class HelloWorld {
        public static void main(String[] args) {
            System.out.println(\"Hello, World of comments /*This is not a comment*/ // Neither is this\"); 
            //  This is a comment
            /*
                This is a multi-line comment
            */
        }
    }
    """
    
    minified_code = minify_java(src_code)
    print("Minified Java Code:")
    print(minified_code)
    
