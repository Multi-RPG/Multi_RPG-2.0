#!/usr/bin/env python3
"""
MealDB Module for Multi-RPG bot
"""
import requests
import logging
from requests.exceptions import HTTPError

log = logging.getLogger("MULTI_RPG")


STR_INGREDIENT = "strIngredient"
STR_MEASURE = "strMeasure"

QUERY = {
    "SEARCH_NAME": "https://www.themealdb.com/api/json/v1/1/search.php?s=",
    "LIST_MEAL_BY_LETTER": "https://www.themealdb.com/api/json/v1/1/search.php?f=",
    "LOOKUP_BY_ID": "https://www.themealdb.com/api/json/v1/1/lookup.php?i=",
    "GET_RANDOM": "https://www.themealdb.com/api/json/v1/1/random.php",
}


class Meal:
    def __init__(self, ID, title, ingredients, instruction, image, source):
        self._id = ID
        self._title = title
        self._ingredients = ingredients
        self._instruction = instruction
        self._image = image
        self._source = source

    def __repr__(self):
        return f"<Meal:\n {self._title}\n" f"{self._ingredients}\n" f"{self._instruction}\n" f"{self._image}>"

    @property
    def title(self):
        return self._title

    @property
    def ingredients(self):
        return self._ingredients

    # TODO: This is unfinished, we're sending the source link for now.
    # Discord doesn't allow message with length greater than 2000.
    # So, this method isn't being used.
    @property
    def instruction(self):
        instruction_list = list()
        # Discord doesn't allow message size greater than 2000
        if len(self._instruction) > 2000:
            # we break it down in two parts
            log.debug(f"Instructions length is {len(self._instruction)} > 2000, splitting in two")
            first_part_len = len(self._instruction) // 2
            second_part_len = len(self._instruction) - first_part_len

            instruction_list.append(self._instruction[0:first_part_len])
            instruction_list.append(self._instruction[second_part_len : len(self._instruction)])
            log.debug(
                f"After splitting: first part {len(instruction_list[0])}, second part is {len(instruction_list[1])}"
            )
            return instruction_list
        elif len(self._instruction) > 4000:
            # we're going to send source file
            log.debug("Instruction is too big... sending source link...")
            return None
        else:
            instruction_list.append(self._instruction)
            return instruction_list

    @property
    def image(self):
        return self._image

    @property
    def source(self):
        return self._source

    def _concatenate(self):
        msg = "Ingredient - Amount\n"
        for ingredients, measure in self._ingredients.items():
            msg += f"{ingredients} - {measure}\n"
        return msg

    def show_meal(self):
        log.debug(
            f"Meal title: {self._title}\n"
            f"Ingredients:\n{self._concatenate()}\n"
            f"Instructions: {self._instruction}\n"
            f"Image: {self._image}"
        )

    def get_formatted_ingredients(self):
        return self._concatenate()


def _parse_ingredients_measure(payload):
    ingredients = list()
    measure = list()
    for index in range(1, 21):
        ingredient_key = f"{STR_INGREDIENT}{index}"
        measure_key = f"{STR_MEASURE}{index}"
        ingredients.append(payload["meals"][0][ingredient_key])
        measure.append(payload["meals"][0][measure_key])

    def is_not_none_or_empty(item):
        return item != "" and item is not None

    # remove empty strings and None
    ingredients = list(filter(is_not_none_or_empty, ingredients))
    measure = list(filter(is_not_none_or_empty, measure))
    assert len(ingredients) == len(measure)
    ingredients = dict(zip(ingredients, measure))
    return ingredients


def _get_meal():
    try:
        # response = requests.get(f"{QUERY['SEARCH_NAME']}{content}")
        response = requests.get(QUERY["GET_RANDOM"])
        response.raise_for_status()

        payload = response.json()
        # print(f"{payload['meals']}")
        # print(f"{payload['meals'][0]}")

        ID = payload["meals"][0]["idMeal"]
        title = payload["meals"][0]["strMeal"]
        ingredients = _parse_ingredients_measure(payload)
        instruction = payload["meals"][0]["strInstructions"]
        image = payload["meals"][0]["strMealThumb"]
        source = payload["meals"][0]["strSource"]
        return Meal(ID, title, ingredients, instruction, image, source)

    except HTTPError as http_err:
        log.debug(f"HTTP error occured: {http_err}")
    except Exception as err:
        log.debug(f"Other error occured: {err}")
    else:
        log.debug("\nWe got a response: Success")


def get_meal():
    """
    If an exception is thrown, it retuns None,
    so, keeps asking until _get_meal doesn't return None.
    """
    while True:
        meal = _get_meal()
        if meal is None:
            continue
        return meal


# if __name__ == "__main__":
#     meal = get_meal()
#     meal.show_meal()
