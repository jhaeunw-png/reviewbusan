import os
import runpy


os.environ["TOURISM_TARGET_YEAR"] = "2025"
runpy.run_path("src/visualization/04_국가별_누적_외국인_방문객.py", run_name="__main__")
