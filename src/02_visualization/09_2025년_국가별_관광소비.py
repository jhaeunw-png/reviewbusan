import os
import runpy


os.environ["TOURISM_TARGET_YEAR"] = "2025"
runpy.run_path("src/visualization/02_국가별_누적_관광소비.py", run_name="__main__")
