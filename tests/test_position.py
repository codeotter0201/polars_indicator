import polars as pl
from polars_indicator import (
    clean_enex_position_ids,
    clean_entries,
    clean_exits,
    reshape_position_id_array,
)


class TestPosition:
    def test_clean_enex_position_multi_entries(self):
        """測試多個連續進場信號"""
        df = pl.DataFrame(
            {
                "entry": [False, True, True, True, False],
                "exit": [False, False, False, False, True],
            }
        )

        result = df.with_columns(
            entries_out=clean_entries("entry", "exit", True),
            exits_out=clean_exits("entry", "exit", True),
            positions_out=clean_enex_position_ids("entry", "exit", True),
        )

        # 驗證結果
        entries_out = result["entries_out"].to_list()
        exits_out = result["exits_out"].to_list()
        positions_out = result["positions_out"].to_list()

        assert entries_out == [False, True, False, False, False]
        assert exits_out == [False, False, False, False, True]
        assert positions_out == [-1, 0, 0, 0, 0]

    def test_clean_enex_position_multi_exits(self):
        """測試多個連續出場信號"""
        df = pl.DataFrame(
            {
                "entry": [False, True, False, False, False],
                "exit": [False, False, False, True, True],
            }
        )

        result = df.with_columns(
            entries_out=clean_entries("entry", "exit", True),
            exits_out=clean_exits("entry", "exit", True),
            positions_out=clean_enex_position_ids("entry", "exit", True),
        )

        entries_out = result["entries_out"].to_list()
        exits_out = result["exits_out"].to_list()
        positions_out = result["positions_out"].to_list()

        assert entries_out == [False, True, False, False, False]
        assert exits_out == [False, False, False, True, False]
        assert positions_out == [-1, 0, 0, 0, -1]

    def test_clean_enex_position_entry_first_true(self):
        """測試進場和出場同時發生且 entry_first=True"""
        df = pl.DataFrame(
            {
                "entry": [False, True, True, False, False],
                "exit": [False, True, False, True, True],
            }
        )

        result = df.with_columns(
            entries_out=clean_entries("entry", "exit", True),
            exits_out=clean_exits("entry", "exit", True),
            positions_out=clean_enex_position_ids("entry", "exit", True),
        )

        entries_out = result["entries_out"].to_list()
        exits_out = result["exits_out"].to_list()
        positions_out = result["positions_out"].to_list()

        assert entries_out == [False, True, False, False, False]
        assert exits_out == [False, False, False, True, False]
        assert positions_out == [-1, 0, 0, 0, -1]

    def test_clean_enex_position_entry_first_false(self):
        """測試進場和出場同時發生且 entry_first=False"""
        df = pl.DataFrame(
            {
                "entry": [False, True, True, True, False],
                "exit": [False, True, False, True, True],
            }
        )

        result = df.with_columns(
            entries_out=clean_entries("entry", "exit", False),
            exits_out=clean_exits("entry", "exit", False),
            positions_out=clean_enex_position_ids("entry", "exit", False),
        )

        entries_out = result["entries_out"].to_list()
        exits_out = result["exits_out"].to_list()
        positions_out = result["positions_out"].to_list()

        assert entries_out == [False, False, True, False, False]
        assert exits_out == [False, False, False, True, False]
        assert positions_out == [-1, -1, 0, 0, -1]

    def test_clean_enex_position_multiple_trades(self):
        """測試多筆交易的位置ID設定"""
        df = pl.DataFrame(
            {
                "entry": [
                    False,
                    True,
                    False,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                ],
                "exit": [
                    False,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                    False,
                    True,
                ],
            }
        )

        result = df.with_columns(
            positions_out=clean_enex_position_ids("entry", "exit", True),
        )

        positions_out = result["positions_out"].to_list()
        assert positions_out == [-1, 0, 0, 0, 0, -1, 1, 1, 1, 1]

    def test_clean_enex_position_exit_first(self):
        """測試出場信號先於進場信號"""
        df = pl.DataFrame(
            {
                "entry": [
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                ],
                "exit": [
                    False,
                    True,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                    False,
                    True,
                ],
            }
        )

        result = df.with_columns(
            entries_out=clean_entries("entry", "exit", True),
            exits_out=clean_exits("entry", "exit", True),
            positions_out=clean_enex_position_ids("entry", "exit", True),
        )

        entries_out = result["entries_out"].to_list()
        exits_out = result["exits_out"].to_list()
        positions_out = result["positions_out"].to_list()

        assert entries_out == [
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            False,
            False,
            False,
        ]
        assert exits_out == [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
        ]
        assert positions_out == [-1, -1, -1, -1, -1, -1, 0, 0, 0, 0]

    def test_clean_enex_position_empty_dataframe(self):
        """測試空DataFrame處理"""
        df = pl.DataFrame(
            {
                "entry": [],
                "exit": [],
            },
            schema={"entry": pl.Boolean, "exit": pl.Boolean},
        )

        result = df.with_columns(
            entries_out=clean_entries("entry", "exit", True),
            exits_out=clean_exits("entry", "exit", True),
            positions_out=clean_enex_position_ids("entry", "exit", True),
        )

        assert result.height == 0

    def test_reshape_position_id_array(self):
        """測試 reshape_position_id_array 函數"""
        df = pl.DataFrame(
            {
                "position_id": [0, 1, 2],
                "entry_idx": [1, 3, 6],
                "exit_idx": [2, 4, 8],
            }
        )

        # 使用 select 而不是 with_columns，因為這是聚合操作
        result = df.select(
            reshape_position_id_array(10, "position_id", "entry_idx", "exit_idx").alias(
                "position_array"
            )
        )

        position_array = result["position_array"].to_list()
        expected = [-1, 0, 0, 1, 1, -1, 2, 2, 2, -1]
        assert position_array == expected

    def test_reshape_position_id_array_edge_cases(self):
        """測試邊界情況"""
        df = pl.DataFrame(
            {
                "position_id": [0],
                "entry_idx": [0],
                "exit_idx": [2],
            }
        )

        # 使用 select 而不是 with_columns，因為這是聚合操作
        result = df.select(
            reshape_position_id_array(3, "position_id", "entry_idx", "exit_idx").alias(
                "position_array"
            )
        )

        position_array = result["position_array"].to_list()
        expected = [0, 0, 0]
        assert position_array == expected
