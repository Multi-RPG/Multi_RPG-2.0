#!/usr/bin/env python3
"""
MealDB Module for Multi-RPG bot
"""
import requests
import logging
from requests.exceptions import HTTPError

log = logging.getLogger("MULTI_RPG")


class MealValue:
    """Constants to access items in the payload sent by the API"""

    meal_id = "idMeal"
    title = "strMeal"
    ingredient = "strIngredient"
    measure = "strMeasure"
    instructions = "strInstructions"
    image = "strMealThumb"
    source = "strSource"


class Query:
    """Available queries"""

    search_by_name = "https://www.themealdb.com/api/json/v1/1/search.php?s="
    search_by_letter = "https://www.themealdb.com/api/json/v1/1/search.php?f="
    search_by_id = "https://www.themealdb.com/api/json/v1/1/lookup.php?i="
    search_by_category = "https://www.themealdb.com/api/json/v1/1/filter.php?c="

    get_random = "https://www.themealdb.com/api/json/v1/1/random.php"


class Meal:
    meal = "meals"

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
        ingredient_key = f"{MealValue.ingredient}{index}"
        measure_key = f"{MealValue.measure}{index}"
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
        # response = requests.get(f"{Query.search_by_name}{name}")
        response = requests.get(Query.get_random)
        response.raise_for_status()

        payload = response.json()
        # print(f"{payload[Meal.meal]}")
        # print(f"{payload[Meal.meal][0]}")

        ID = payload[Meal.meal][0][MealValue.meal_id]
        title = payload[Meal.meal][0][MealValue.title]
        ingredients = _parse_ingredients_measure(payload)
        instruction = payload[Meal.meal][0][MealValue.instructions]
        image = payload[Meal.meal][0][MealValue.image]
        source = payload[Meal.meal][0][MealValue.source]
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
