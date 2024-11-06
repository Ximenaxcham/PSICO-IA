import pygame
import random
import time
import csv
import statistics  # Para calcular la mediana

# Initialize Pygame
pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set fonts
large_font = pygame.font.Font(None, 60)
medium_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)

# Define more complex math problems (addition, subtraction, multiplication, and division)
math_problems = [
    ("12 + 8", 20), ("25 - 9", 16), ("7 * 6", 42), ("36 / 6", 6),
    ("15 + 24", 39), ("9 * 4", 36), ("18 / 3", 6), ("48 - 17", 31),
    ("3 * 8", 24), ("56 / 7", 8), ("12 * 2", 24), ("9 + 7", 16),
    ("81 / 9", 9), ("72 / 8", 9), ("45 - 18", 27), ("63 - 36", 27),
]

# Define the letters to be used
letters = ['B', 'F', 'Q', 'L', 'K', 'P', 'R', 'S', 'T', 'M', 'Z', 'H', 'C']

# Function to display text on screen
def display_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to display math problem and randomly present true/false options
def display_math_problem(problem, correct_answer):
    screen.fill(WHITE)
    start_time = time.time()
    time_limit = 5  # 5 seconds limit

    # Randomly decide if the displayed answer will be correct or incorrect
    is_correct_display = random.choice([True, False])
    displayed_answer = correct_answer if is_correct_display else correct_answer + random.randint(-10, 10)

    display_text(f"{problem} = {displayed_answer}", large_font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Draw True/False buttons
    true_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 100, 50)
    false_button = pygame.Rect(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 100, 100, 50)
    pygame.draw.rect(screen, GREEN, true_button)
    pygame.draw.rect(screen, RED, false_button)
    display_text("True", medium_font, BLACK, true_button.centerx, true_button.centery)
    display_text("False", medium_font, BLACK, false_button.centerx, false_button.centery)
    
    pygame.display.flip()

    # Wait for the participant to click True or False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                elapsed_time = time.time() - start_time
                if true_button.collidepoint(event.pos):
                    return is_correct_display, displayed_answer, elapsed_time
                elif false_button.collidepoint(event.pos):
                    return not is_correct_display, displayed_answer, elapsed_time

        # Check if time is up
        if time.time() - start_time > time_limit:
            return False, displayed_answer, time_limit  # Consider it incorrect if time runs out

# Function to display a letter for a given amount of time
def display_letter(letter):
    screen.fill(WHITE)
    display_text(letter, large_font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    time.sleep(1)

# Function to collect recall responses from the participant, with backspace support for letter sequence
def recall_phase():
    screen.fill(WHITE)
    display_text("Recall the letters (type the sequence)", small_font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
    pygame.display.flip()

    answer = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return answer.upper()  # Return the full sequence typed by the user
                elif event.key == pygame.K_BACKSPACE:  # Support for deleting the last letter
                    answer = answer[:-1]  # Remove the last character
                elif event.unicode.isalpha():
                    answer += event.unicode
                # Update the display with the current recalled sequence
                screen.fill(WHITE)
                display_text("Recall the letters (type the sequence)", small_font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
                display_text(answer.upper(), medium_font, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                pygame.display.flip()

# Function to count how many letters were incorrect and return the incorrect letters
def count_incorrect_letters(correct_sequence, recalled_sequence):
    incorrect_count = 0
    incorrect_letters = ''
    for correct_letter, recalled_letter in zip(correct_sequence, recalled_sequence):
        if correct_letter != recalled_letter:
            incorrect_count += 1
            incorrect_letters += recalled_letter if recalled_letter else '_'
    return incorrect_count, incorrect_letters

# Function to calculate math accuracy percentage
def calculate_math_accuracy(total_math_attempted, total_correct_math):
    if total_math_attempted > 0:
        return (total_correct_math / total_math_attempted) * 100
    return 0

# Function to show initial instructions
def show_initial_instructions():
    screen.fill(WHITE)
    instructions = [
        "This experiment consists of two parts:",
        "1. A practice session with 3 rounds.",
        "2. A real test with 10 rounds.",
        "You'll have 5 seconds to respond to the math problems.",
        "Remember the set of letters.",
        "Answer as quickly and accurately as possible.",
        "Press any key to begin the practice test."
    ]
    
    y_offset = 200
    for line in instructions:
        display_text(line, small_font, BLACK, SCREEN_WIDTH // 2, y_offset)
        y_offset += 50

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False

# Function to run a test (either practice or real)
def run_test(num_rounds=3, practice=False):
    total_incorrect_math = 0
    total_correct_math = 0
    total_math_attempted = 0
    total_incorrect_letters = 0
    all_times = []  # Lista para almacenar los tiempos de respuesta

    # Open a CSV file to save the results
    with open('ospan_results.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header if it's the first time (only in non-practice mode)
        if not practice:
            writer.writerow(["Math Question", "Displayed Answer", "Math Correct?", "Original Letters", "Recalled Letters", "Incorrect Letters", "Math Accuracy (%)", "Time Taken (s)", "Cumulative Accuracy (%)", "Median Time (s)"])
        
        for round_number in range(1, num_rounds + 1):
            correct_letters = []
            incorrect_math_in_round = 0
            incorrect_letters_in_round = 0

            # Randomly determine the number of letters for this round (3 to 7 letters)
            num_letters = random.randint(3, 7)

            for i in range(num_letters):
                math_problem, correct_answer = random.choice(math_problems)
                letter = random.choice(letters)

                # Display the math problem and get the response (True/False)
                math_correct, displayed_answer, time_taken = display_math_problem(math_problem, correct_answer)
                total_math_attempted += 1
                all_times.append(time_taken)

                if math_correct:
                    total_correct_math += 1
                else:
                    total_incorrect_math += 1
                    incorrect_math_in_round += 1

                display_letter(letter)
                correct_letters.append(letter)

            correct_sequence = ''.join(correct_letters)
            recalled_sequence = recall_phase()

            incorrect_letters_count, incorrect_letters = count_incorrect_letters(correct_sequence, recalled_sequence)
            total_incorrect_letters += incorrect_letters_count
            incorrect_letters_in_round += incorrect_letters_count

            # Calculate math accuracy percentage
            math_accuracy = calculate_math_accuracy(total_math_attempted, total_correct_math)
            cumulative_accuracy = calculate_math_accuracy(total_math_attempted, total_correct_math)

            # Calculate median time taken
            median_time = statistics.median(all_times) if all_times else 0

            # Write round data to the CSV file (in non-practice mode)
            if not practice:
                writer.writerow([math_problem, displayed_answer, math_correct, correct_sequence, recalled_sequence, incorrect_letters, math_accuracy, time_taken, cumulative_accuracy, median_time])

            round_feedback = f"Round {round_number} complete! Math problems wrong: {incorrect_math_in_round}, Letters wrong: {incorrect_letters_in_round}, Cumulative Accuracy: {cumulative_accuracy:.2f}%, Median Time: {median_time:.2f}s"
            screen.fill(WHITE)
            display_text(round_feedback, small_font, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.display.flip()
            time.sleep(3)

    feedback_text = f"Test Complete! You got {total_incorrect_math} math problems and {total_incorrect_letters} letters wrong."
    screen.fill(WHITE)
    display_text(feedback_text, small_font, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    time.sleep(5)

# Main OSPAN experiment loop
def ospan_experiment():
    show_initial_instructions()
    run_test(num_rounds=3, practice=True)
    run_test(num_rounds=10, practice=False)

# Run the experiment
ospan_experiment()

# Quit Pygame
pygame.quit()
