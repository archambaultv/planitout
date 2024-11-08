from planitout.lesson_plan import create_null_dict, generate_latex_content, LessonPlan, \
     compile_latex
from pathlib import Path
from yaml import safe_dump


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
    skeleton = create_null_dict(LessonPlan)
    yaml_file = LessonPlan.from_yaml(lesson_plan_yaml_file)

    # Write skeleton dict to file
    with open("skeleton.yaml", "w") as f:
        f.write(safe_dump(skeleton, sort_keys=False))

    for key in yaml_file.model_dump().keys():
        assert key in skeleton
