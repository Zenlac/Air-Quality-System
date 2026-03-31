#!/usr/bin/env python3
"""
Script to extract text from Questions.pdf
"""

import os
import sys

def try_pdf_extraction():
    """Try multiple methods to extract PDF content"""
    
    pdf_path = "Basis files/Questions.pdf"
    
    # Method 1: Try basic text extraction
    try:
        with open(pdf_path, 'rb') as file:
            content = file.read()
            
        # Look for text patterns in binary data
        text_parts = []
        current_text = ""
        
        for i, byte in enumerate(content):
            if 32 <= byte <= 126:  # Printable ASCII
                current_text += chr(byte)
            else:
                if current_text.strip():
                    text_parts.append(current_text.strip())
                current_text = ""
        
        if current_text.strip():
            text_parts.append(current_text.strip())
            
        full_text = "\n".join(text_parts)
        
        # Save extracted text
        with open("extracted_questions.txt", "w", encoding="utf-8") as f:
            f.write("EXTRACTED CONTENT FROM Questions.pdf:\n")
            f.write("=" * 50 + "\n\n")
            f.write(full_text)
            
        print("Successfully extracted content to extracted_questions.txt")
        return True
        
    except Exception as e:
        print(f"Method 1 failed: {e}")
        return False

def try_hex_analysis():
    """Try to analyze PDF as hex to find text patterns"""
    try:
        with open("Basis files/Questions.pdf", 'rb') as file:
            content = file.read()
        
        # Look for common text patterns
        hex_content = content.hex()
        
        # Search for common question words
        question_words = ["What", "How", "When", "Where", "Why", "Which", "Who", "error", "Error", "fix", "Fix"]
        
        found_text = []
        for word in question_words:
            word_hex = word.encode('utf-8').hex()
            if word_hex in hex_content.lower():
                found_text.append(word)
        
        if found_text:
            with open("hex_analysis.txt", "w") as f:
                f.write("HEX ANALYSIS RESULTS:\n")
                f.write("=" * 30 + "\n")
                f.write(f"Found question-related words: {found_text}\n")
                f.write(f"PDF size: {len(content)} bytes\n")
                f.write(f"First 1000 hex chars: {hex_content[:1000]}\n")
            
            print("Hex analysis completed - saved to hex_analysis.txt")
            return True
        else:
            print("No question words found in hex analysis")
            return False
            
    except Exception as e:
        print(f"Hex analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("Attempting to extract Questions.pdf content...")
    
    success1 = try_pdf_extraction()
    if not success1:
        success2 = try_hex_analysis()
        
    if not success1 and not success2:
        print("All extraction methods failed")
        print("Please check if the PDF file is corrupted or password-protected")
        sys.exit(1)
