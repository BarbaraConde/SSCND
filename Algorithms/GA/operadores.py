import numpy as np
import random


def crossover(V1, V2, numberOfPlants, numberOfDepots, numberofPeriods):
    # Linear order crossover

    totalLength = V1.shape[1]
    firstLength = 2*(numberOfPlants + numberOfDepots)
    offspring = np.zeros((2, numberofPeriods, totalLength))

    # first point
    position = random.randint(1, firstLength)

    offspring[0, :, 0: position] = V1[:, 0: position]
    offspring[1, :, 0: position] = V2[:, 0: position]

    offspring[0, :, position: firstLength] = V2[:, position: firstLength]
    offspring[1, :, position: firstLength] = V1[:, position: firstLength]

    # second point
    position2 = random.randint(firstLength + 1, totalLength)

    offspring[0, :, firstLength: position2] = V1[:, firstLength: position2]
    offspring[1, :, firstLength: position2] = V2[:, firstLength: position2]

    # preenche o restante dos elementos dos filhos, de acordo com a ordem linear do outro pai

    for t in range(numberofPeriods):
        s1 = position2
        s2 = position2
        for i in range(firstLength, totalLength):
            check1 = 0
            check2 = 0
            for j in range(firstLength, position2):
                if V1[t, i] != 0:
                    if V1[t, i] == offspring[1, t, j]:
                        check1 = 1
                if V2[t, i] != 0:
                    if V2[t, i] == offspring[0, t, j]:
                        check2 = 1

            if s1 < totalLength:
                if check2 == 0:
                    offspring[0, t, s1] = V2[t, i]
                    s1 = s1 + 1
            if s2 < totalLength:
                if check1 == 0:
                    offspring[1, t, s2] = V1[t, i]
                    s2 = s2 + 1

    return offspring


def mutation(V, numberOfPlants, numberOfDepots, numberOfPeriods):
    totalLength = V.shape[1]
    firstLength = numberOfPlants
    secondLength = numberOfPlants + numberOfDepots
    thirdLength = 2*(numberOfPlants + numberOfDepots)
    result = np.ones((numberOfPeriods, totalLength)) * np.inf

    # choose positions
    position1 = random.randint(0, firstLength - 1)
    new_position1 = random.randint(0, firstLength - 1)
    position2 = random.randint(firstLength, secondLength - 1)
    new_position2 = random.randint(firstLength, secondLength - 1)
    position3 = random.randint(secondLength, thirdLength - 1)
    new_position3 = random.randint(secondLength, thirdLength - 1)
    position4 = random.randint(thirdLength, totalLength - 1)
    new_position4 = random.randint(thirdLength, totalLength - 1)
    #
    # while new_position1 == position1:
    #     new_position1 = random.randint(0, firstLength - 1)
    # while new_position2 == position2:
    #     new_position2 = random.randint(firstLength, secondLength - 1)
    # while new_position3 == position3:
    #     new_position3 = random.randint(secondLength, totalLength - 1)


    # choose size of array
    maxLength1 = min(firstLength - position1, firstLength - new_position1)
    sectionLength1 = random.randint(1, maxLength1)
    maxLength2 = min(secondLength - position2, secondLength - new_position2)
    sectionLength2 = random.randint(1, maxLength2)
    maxLength3 = min(thirdLength - position3, thirdLength - new_position3)
    sectionLength3 = random.randint(1, maxLength3)
    maxLength4 = min(totalLength - position4, totalLength - new_position4)
    sectionLength4 = random.randint(1, maxLength4)

    # change place of selected array
    result[:, new_position1:new_position1 + sectionLength1] = V[:, position1:position1 + sectionLength1]
    result[:, new_position2:new_position2 + sectionLength2] = V[:, position2:position2 + sectionLength2]
    result[:, new_position3:new_position3 + sectionLength3] = V[:, position3:position3 + sectionLength3]
    result[:, new_position4:new_position4 + sectionLength4] = V[:, position4:position4 + sectionLength4]

    # fill out the rest of the chromosome
    for t in range(numberOfPeriods):
        x = 0
        y = 0
        while x < firstLength and y < firstLength:

            if x == new_position1:
                x = x + sectionLength1

            if y == position1:
                y = y + sectionLength1

            if x < firstLength and y < firstLength:

                result[t, x] = V[t, y]
                x = x + 1
                y = y + 1

        p = firstLength
        q = firstLength
        while p < secondLength and q < secondLength:
            if p == new_position2:
                p = p + sectionLength2

            if q == position2:
                q = q + sectionLength2

            if p < secondLength and q < secondLength:
                result[t, p] = V[t, q]
                p = p + 1
                q = q + 1


        z = secondLength
        w = secondLength
        while z < thirdLength and w < thirdLength:
            if z == new_position3:
                z = z + sectionLength3

            if w == position3:
                w = w + sectionLength3

            if z < thirdLength and w < thirdLength:

                result[t, z] = V[t, w]
                z = z + 1
                w = w + 1

        alpha = thirdLength
        beta = thirdLength
        while alpha < totalLength and beta < totalLength:
            if alpha == new_position4:
                alpha += sectionLength4

            if beta == position4:
                beta += sectionLength4

            if alpha < totalLength and beta < totalLength:
                result[t, alpha] = V[t, beta]
                alpha += 1
                beta += 1

    return result

