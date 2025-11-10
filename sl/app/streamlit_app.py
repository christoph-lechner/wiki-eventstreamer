# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

import streamlit as st

dir_path = Path(__file__).parent


# Note that this needs to be in a method so we can have an e2e playwright test.
def run() -> None:
    page = st.navigation(
        {
            "Pages": [
                st.Page(
                    dir_path / "hello.py", title="Hello", icon=":material/waving_hand:"
                ),
                st.Page(
                    dir_path / "db_stat.py",
                    title="database statistics",
                    icon=":material/table:",
                ),
                st.Page(
                    dir_path / "top_edits.py",
                    title="top20",
                    icon=":material/table:",
                ),
                #st.Page(
                #    dir_path / "dataframe_demo.py",
                #    title="DataFrame demo",
                #    icon=":material/table:",
                #),
                #st.Page(
                #    dir_path / "plotting_demo.py",
                #    title="Plotting demo",
                #    icon=":material/show_chart:",
                #),
            ]
        }
    )
    page.run()


if __name__ == "__main__":
    run()
