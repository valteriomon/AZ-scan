import pytest
from core.panorama_tools import GridSets  # Assuming GridSets is in the gridsets module
import tests.gridsets_data as data

def sort(results):
    return sorted([sorted(item) for item in results])

# Test GridSets.quadruplets
def test_quadruplets_3x4():
    result = GridSets.quadruplets(data.grids["full"]["3x4"])
    expected = [
        ["A1", "A2", "B1", "B2"],
        ["A2", "A3", "B2", "B3"],
        ["A3", "A4", "B3", "B4"],
        ["B1", "B2", "C1", "C2"],
        ["B2", "B3", "C2", "C3"],
        ["B3", "B4", "C3", "C4"]
    ]
    assert sort(result) == sort(expected)

# Test GridSets.inverted_diagonal_couples
def test_inverted_diagonal_couples_3x4():
    result = GridSets.inverted_diagonal_couples(data.grids["full"]["3x4"])
    expected = [
        ["A2", "B1"],
        ["A3", "B2"],
        ["A4", "B3"],
        ["B1", "C2"],
        ["B2", "C3"],
        ["B3", "C4"]
    ]
    assert sort(result) == sort(expected)

# Test GridSets.last_adjacent_neighbours
def test_last_adjacent_neighbours():
    def test_grid_simulation(grids):
        return [GridSets.last_adjacent_neighbours(grid) for grid in grids]

    # Test case 1: 3x4 grid simulation
    result1 = test_grid_simulation(data.grids["real_time_simulation"]["3x4"])
    expected1 = [
        [], # first scan should return empty set
        ["A2", "A1"],
        ["A3", "A2"],
        ["A4", "A3"],
        ["B4", "A4"],
        ["B3", "B4", "A3"],
        ["B2", "B3", "A2"],
        ["B1", "B2", "A1"],
        ["C1", "B1"],
        ["C2", "C1", "B2"],
        ["C3", "C2", "B3"],
        ["C4", "C3", "B4"]
    ]
    assert sort(result1) == sort(expected1)

    # Test case 2: 4x3 grid simulation
    result2 = test_grid_simulation(data.grids["real_time_simulation"]["4x3"])
    expected2 = [
        [], # first scan should return empty set
        ["A2", "A1"],
        ["A3", "A2"],
        ["B3", "A3"],
        ["B2", "B3", "A2"],
        ["B1", "B2", "A1"],
        ["C1", "B1"],
        ["C2", "C1", "B2"],
        ["C3", "C2", "B3"],
        ["D3", "C3"],
        ["D2", "D3", "C2"],
        ["D1", "D2", "C1"]
    ]
    assert sort(result2) == sort(expected2)

    # Test case 3: 2x5 grid simulation
    result3 = test_grid_simulation(data.grids["real_time_simulation"]["2x5"])
    expected3 = [
        [], # first scan should return empty set
        ["A2", "A1"],
        ["A3", "A2"],
        ["A4", "A3"],
        ["A5", "A4"],
        ["B5", "A5"],
        ["B4", "B5", "A4"],
        ["B3", "B4", "A3"],
        ["B2", "B3", "A2"],
        ["B1", "B2", "A1"]
    ]
    assert sort(result3) == sort(expected3)

    # Test case 4: 5x2 grid simulation
    result4 = test_grid_simulation(data.grids["real_time_simulation"]["5x2"])
    expected4 = [
        [], # first scan should return empty set
        ["A2", "A1"],
        ["B2", "A2"],
        ["B1", "B2", "A1"],
        ["C1", "B1"],
        ["C2", "C1", "B2"],
        ["D2", "C2"],
        ["D1", "D2", "C1"],
        ["E1", "D1"],
        ["E2", "E1", "D2"]

    ]
    assert sort(result4) == sort(expected4)

