import random
import numpy as np
import math 
from random import choice
import statistics
from typing import List


class Solution:

    def solveSudoku(self, board: List[List[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        f = open("demofile2.txt", "a")
        seed = 8
        np.random.seed(seed)
        random.seed(seed)
        n = 9
        sudoku = [[0]*n for _ in range(n)]
        counter = 0
        for i in range(n):
            for j in range(n):
                if board[i][j] == '.':
                    sudoku[i][j] = 0
                    counter += 1
                else:
                    sudoku[i][j] = int(board[i][j])
        sudoku = np.array(sudoku)
        print(counter)

        solutionFound = 0
        while solutionFound == 0:
            decreaseFactor = 0.99
            stuckCount = 0
            fixedSudoku = np.copy(sudoku)
            self.FixSudokuValues(fixedSudoku)
            listOfBlocks = self.CreateList3x3Blocks()
            tmpSudoku = self.RandomlyFill3x3Blocks(sudoku, listOfBlocks)
            sigma = self.CalculateInitialSigma(sudoku, fixedSudoku, listOfBlocks)
            score = self.CalculateNumberOfErrors(tmpSudoku)
            iterations = self.ChooseNumberOfItterations(fixedSudoku)
            if score <= 0:
                solutionFound = 1

            total_iteration = 0
            while solutionFound == 0:
                previousScore = score
                for _ in range(0, iterations):
                    total_iteration += 1
                    newState = self.ChooseNewState(tmpSudoku, fixedSudoku, listOfBlocks, sigma)
                    tmpSudoku = newState[0]
                    scoreDiff = newState[1]
                    score += scoreDiff
                    if score <= 0:
                        solutionFound = 1
                        break

                sigma *= decreaseFactor    # sigma is the Temperature
                f.write(str(score) + '\n')
                if score <= 0:
                    solutionFound = 1
                    break
                if score >= previousScore:
                    stuckCount += 1
                else:
                    stuckCount = 0
                if stuckCount > 160:
                    f.write('RESET!\n')
                    sigma += 1
                    stuckCount = 0
                    print(f'reset at iteration {total_iteration}')
                if self.CalculateNumberOfErrors(tmpSudoku) == 0:
                    break

        for i in range(n):
            for j in range(n):
                board[i][j] = str(tmpSudoku[i][j])


    def FixSudokuValues(self, fixed_sudoku):
        for i in range(0,9):
            for j in range(0,9):
                if fixed_sudoku[i,j] != 0:
                    fixed_sudoku[i,j] = 1
        
        return fixed_sudoku
        
    # Cost Function
    def CalculateNumberOfErrors(self, sudoku):
        numberOfErrors = 0 
        for i in range(0, 9):
            numberOfErrors += self.CalculateNumberOfErrorsRowColumn(i, i, sudoku)
        return numberOfErrors

    def CalculateNumberOfErrorsRowColumn(self, row, column, sudoku):
        numberOfErrors = (9 - len(np.unique(sudoku[:, column]))) + (9 - len(np.unique(sudoku[row, :])))
        return numberOfErrors

    def CreateList3x3Blocks(self):
        finalListOfBlocks = []
        for r in range(0,9):
            tmpList = []
            block1 = [i + 3*((r)%3) for i in range(0,3)]
            block2 = [i + 3*math.trunc((r)/3) for i in range(0,3)]
            for x in block1:
                for y in block2:
                    tmpList.append([x,y])
            finalListOfBlocks.append(tmpList)
        return finalListOfBlocks

    def RandomlyFill3x3Blocks(self, sudoku, listOfBlocks):
        for block in listOfBlocks:
            for box in block:
                if sudoku[box[0],box[1]] == 0:
                    currentBlock = sudoku[block[0][0]:(block[-1][0]+1), block[0][1]:(block[-1][1]+1)]
                    sudoku[box[0],box[1]] = choice([i for i in range(1, 10) if i not in currentBlock])
        return sudoku

    def SumOfOneBlock(self, sudoku, oneBlock):
        finalSum = 0
        for box in oneBlock:
            finalSum += sudoku[box[0], box[1]]
        return finalSum

    def TwoRandomBoxesWithinBlock(self, fixedSudoku, block):
        while True:
            firstBox = random.choice(block)
            secondBox = choice([box for box in block if box is not firstBox])

            if fixedSudoku[firstBox[0], firstBox[1]] != 1 and fixedSudoku[secondBox[0], secondBox[1]] != 1:
                return [firstBox, secondBox]

    def FlipBoxes(self, sudoku, boxesToFlip):
        proposedSudoku = np.copy(sudoku)
        placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
        proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
        proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
        return proposedSudoku

    def ProposedState(self, sudoku, fixedSudoku, listOfBlocks):
        randomBlock = random.choice(listOfBlocks)

        if self.SumOfOneBlock(fixedSudoku, randomBlock) > 6:  
            return(sudoku, 1, 1)
        boxesToFlip = self.TwoRandomBoxesWithinBlock(fixedSudoku, randomBlock)
        proposedSudoku = self.FlipBoxes(sudoku, boxesToFlip)
        return [proposedSudoku, boxesToFlip]

    def ChooseNewState(self, currentSudoku, fixedSudoku, listOfBlocks, sigma):
        proposal = self.ProposedState(currentSudoku, fixedSudoku, listOfBlocks)
        newSudoku = proposal[0]
        boxesToCheck = proposal[1]
        currentCost = self.CalculateNumberOfErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], currentSudoku) + self.CalculateNumberOfErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], currentSudoku)
        newCost = self.CalculateNumberOfErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], newSudoku) + self.CalculateNumberOfErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], newSudoku)
        costDifference = newCost - currentCost
        rho = math.exp(-costDifference/sigma)
        if np.random.uniform(1, 0, 1) < rho:
            return [newSudoku, costDifference]
        return [currentSudoku, 0]

    def ChooseNumberOfItterations(self, fixed_sudoku):
        numberOfItterations = 0
        for i in range(0, 9):
            for j in range(0, 9):
                if fixed_sudoku[i, j] != 0:
                    numberOfItterations += 1
        return numberOfItterations

    def CalculateInitialSigma(self, sudoku, fixedSudoku, listOfBlocks):
        listOfDifferences = []
        tmpSudoku = sudoku
        for i in range(1, 10):
            tmpSudoku = self.ProposedState(tmpSudoku, fixedSudoku, listOfBlocks)[0]
            listOfDifferences.append(self.CalculateNumberOfErrors(tmpSudoku))
        return statistics.pstdev(listOfDifferences)


# board = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]
board = [[".",".","9","7","4","8",".",".","."],["7",".",".",".",".",".",".",".","."],[".","2",".","1",".","9",".",".","."],[".",".","7",".",".",".","2","4","."],[".","6","4",".","1",".","5","9","."],[".","9","8",".",".",".","3",".","."],[".",".",".","8",".","3",".","2","."],[".",".",".",".",".",".",".",".","6"],[".",".",".","2","7","5","9",".","."]]
# board = [[".",".",".","2",".",".",".","6","3"],["3",".",".",".",".","5","4",".","1"],[".",".","1",".",".","3","9","8","."],[".",".",".",".",".",".",".","9","."],[".",".",".","5","3","8",".",".","."],[".","3",".",".",".",".",".",".","."],[".","2","6","3",".",".","5",".","."],["5",".","3","7",".",".",".",".","8"],["4","7",".",".",".","1",".",".","."]]

s = Solution()
s.solveSudoku(board)
print(board)
