import yaml
from planitout.lesson_plan import generate_latex_content, LessonPlan, \
     compile_latex
from pathlib import Path


def test_read_yaml(lesson_plan_yaml_file: str):
    lesson_plan = LessonPlan.from_yaml(lesson_plan_yaml_file)
    assert (lesson_plan.lesson_info.lesson_title
            == "Révision des fonctions exponentielles et des logarithmes")


def test_generate_latex_content(lesson_plan_yaml_file: str, lesson_plan_tex_file: str):
    lesson_plan = LessonPlan.from_yaml(lesson_plan_yaml_file)
    latex_content = generate_latex_content(lesson_plan)
    # Compare the generated LaTeX content with the expected content
    with open(lesson_plan_tex_file, "r") as f:
        expected_content = f.read()
    assert latex_content == expected_content


def test_generate_latex_content2(lesson_plan_yaml_file: str, lesson_plan_tex_file2: str):
    lesson_plan = LessonPlan.from_yaml(lesson_plan_yaml_file)
    lesson_plan.lesson_info.start_time = None
    lesson_plan.lesson_info.end_time = None
    latex_content = generate_latex_content(lesson_plan)
    # Compare the generated LaTeX content with the expected content
    with open(lesson_plan_tex_file2, "r") as f:
        expected_content = f.read()
    assert latex_content == expected_content


def test_compile_latex(lesson_plan_yaml_file: str, lesson_plan_tex_file: str,
                       tmpdir: str):
    lesson_plan = LessonPlan.from_yaml(lesson_plan_yaml_file)
    latex_content = generate_latex_content(lesson_plan)
    # Generate the LaTeX file in the tmp directory
    with open(f"{tmpdir}/tmp.tex", "w") as f:
        f.write(latex_content)
    compile_latex(f"{tmpdir}/tmp.tex")
    # Check if the PDF file has been generated
    assert Path(f"{tmpdir}/tmp.pdf").exists()


def test_skeleton_yaml(lesson_plan_yaml_file: str):
    skeleton = LessonPlan.to_empty_dict()
    with open(lesson_plan_yaml_file, 'r', encoding='utf-8') as file:
        yaml_data = yaml.safe_load(file)

    # Assert both dict have the same keys at each level
    def compare_keys(dict1: dict, dict2: dict):
        assert dict1.keys() == dict2.keys()
        for key in dict1.keys():
            if isinstance(dict1[key], dict):
                compare_keys(dict1[key], dict2[key])
            if isinstance(dict1[key], list):
                if isinstance(dict1[key][0], dict):
                    compare_keys(dict1[key][0], dict2[key][0])
    compare_keys(skeleton, yaml_data)
