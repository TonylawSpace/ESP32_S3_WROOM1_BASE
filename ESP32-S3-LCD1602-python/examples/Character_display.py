import LCD1602  # Import the LCD1602 module
import time  # Import the time module for delays

# Initialize LCD with 16 columns and 2 rows
lcd = LCD1602.LCD1602(16, 2)

try:
    # Set the cursor to column 0, row 0
    lcd.setCursor(0, 0)
    # Display the text "Waveshare" on the first row
    lcd.printout("Waveshare")

    # Set the cursor to column 0, row 1
    lcd.setCursor(0, 1)
    # Display the text "Hello World!" on the second row
    lcd.printout("Hello World!")
    

except KeyboardInterrupt:  # Handle user interruption (Ctrl+C)
    # Clear the LCD display
    lcd.clear()
    # Delete the LCD object to free resources
    del lcd


