# Defining a set of functions to load static text data, which is necessary for many mini-games in Games Module
# This Class will store that data from text files into memory (emoji lists, hangman words, hangman art)
# Therefore since it is in memory, the Games module will not need to re-read the files every time a function is called
class GamesMemLoader:
    def get_hangman_art(self):
        # prepare array of hangman art
        art_array = []
        with open(r"db_and_words\hangmen.txt") as my_file:
            for line in my_file:
                art_array.append(line)

        # convert respective list index-ranges to string with ''.join
        # the resulting art_array[0-6] will represent each stage of hangman
        art_array[0] = "".join(art_array[0:6])
        art_array[1] = "".join(art_array[7:13])
        art_array[2] = "".join(art_array[14:20])
        art_array[3] = "".join(art_array[21:27])
        art_array[4] = "".join(art_array[28:34])
        art_array[5] = "".join(art_array[35:41])
        art_array[6] = "".join(art_array[42:49])
        return art_array

    def get_hangman_words(self):
        # only read words file once so we won't have to re-open the file every game call
        words_file = open(r"db_and_words\words.txt", "r")
        words = words_file.readlines()
        words_file.close()
        return words

    def get_tier_list(self, file_path):
        with open(file_path, "r") as lines:
            high_tier = []
            mid_tier = []
            low_tier = []

            current_tier = ""

            for line in lines:
                line = line.rstrip("\n")
                if line == "HIGH-TIER-LIST":
                    current_tier = "high"
                    continue
                if line == "MEDIUM-TIER-LIST":
                    current_tier = "med"
                    continue
                if line == "LOW-TIER-LIST":
                    current_tier = "low"
                    continue
                if current_tier == "high":
                    high_tier.append(line)
                elif current_tier == "med":
                    mid_tier.append(line)
                elif current_tier == "low":
                    low_tier.append(line)
            return high_tier, mid_tier, low_tier
