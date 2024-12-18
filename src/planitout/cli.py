import argparse
import yaml
from planitout.lesson_plan import LatexOptions, LessonPlan, compile_latex, \
    generate_latex_content
from planitout.beamer import beamer_template


def main() -> None:
    args = parse_args()

    if args.command == 'plan':
        create_tex_plan(args)

    elif args.command == 'new':
        write_skeleton_yaml(args)

    elif args.command == 'beamer':
        write_beamer_template(args)


def write_beamer_template(args) -> None:
    with open(args.file_name, 'w', encoding='utf-8') as file:
        file.write(beamer_template())


def create_tex_plan(args):
    lesson_yaml = args.lesson_yaml
    lesson_tex = args.output if args.output else lesson_yaml.replace('.yaml', '.tex')
    opt = LatexOptions(one_page_per_activity=args.single_page)

    lesson_plan = LessonPlan.from_yaml(lesson_yaml)
    latex_content = generate_latex_content(lesson_plan, opt=opt)

    with open(lesson_tex, 'w', encoding='utf-8') as file:
        file.write(latex_content)

    if args.compile:
        compile_latex(lesson_tex)


def parse_args():
    parser = argparse.ArgumentParser(description='Outils pour gérer les plans de leçon.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subcommand 'plan'
    plan_parser = subparsers.add_parser(
        'plan', help='Générer un plan de leçon LaTeX à partir d\'un fichier YAML.')
    plan_parser.add_argument('lesson_yaml', type=str,
                             help='Chemin vers le fichier YAML de la leçon')
    plan_parser.add_argument('-o', '--output', type=str,
                             help='Chemin vers le fichier LaTeX de sortie', default=None)
    plan_parser.add_argument('-s', '--single-page', action='store_true',
                             help='Générer une page par activité', default=True)
    plan_parser.add_argument('-c', '--compile', action='store_true',
                             help='Compiler directement le fichier .tex avec LuaLaTeX',
                             default=False)

    # Subcommand 'new'
    new_parser = subparsers.add_parser(
        'new', help='Créer un fichier YAML squelette pour un plan de leçon.')
    new_parser.add_argument('file_name',
                            type=str, help='Nom du fichier YAML à créer')

    # Subcommand 'beamer'
    beamer_parser = subparsers.add_parser(
        'beamer', help='Créer un fichier LaTeX de base pour une présentation Beamer.')
    beamer_parser.add_argument('file_name',
                               type=str, help='Nom du fichier LaTeX à créer')

    return parser.parse_args()


def write_skeleton_yaml(args) -> None:
    # Create a skeleton from the lesson plan Pydantic model
    lesson_plan = LessonPlan.to_empty_dict()

    with open(args.file_name, 'w', encoding='utf-8') as file:
        yaml.dump(lesson_plan, file, allow_unicode=True, sort_keys=False)
