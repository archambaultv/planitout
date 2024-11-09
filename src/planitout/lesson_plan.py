import yaml
from datetime import date as date_type, time, timedelta, datetime
from pydantic import BaseModel, field_validator
import locale
import subprocess
import os

###############################################################################
# Pydantic models for the lesson plan
###############################################################################


class LessonInfo(BaseModel):
    lesson_title: str
    lesson_number: str | None = None
    course: str | None = None
    location: str | None = None
    date: date_type | None = None
    start_time: time | None = None
    end_time: time | None = None
    learning_objectives: str | list[str] | None = None
    materials: str | list[str] | None = None
    curriculum_competencies: str | list[str] | None = None
    curriculum_performance_criteria: str | list[str] | None = None

    @field_validator('lesson_number', mode='before')
    def convert_lesson_number(cls, v):
        return str(v) if v is not None else v

    @classmethod
    def from_dict(cls, data: dict) -> 'LessonInfo':
        """
        Convert a dictionary with keys in French to a LessonInfo object.
        """
        d = {}
        for key, value in data.items():
            if key == 'titre':
                d['lesson_title'] = value
            elif key == 'numéro de leçon':
                d['lesson_number'] = value
            elif key == 'cours':
                d['course'] = value
            elif key == 'lieu':
                d['location'] = value
            elif key == 'date':
                d['date'] = value
            elif key == 'heure de début':
                d['start_time'] = value
            elif key == 'heure de fin':
                d['end_time'] = value
            elif key == 'cible d\'apprentissage':
                d['learning_objectives'] = value
            elif key == 'matériel':
                d['materials'] = value
            elif key == 'compétences du devis':
                d['curriculum_competencies'] = value
            elif key == 'critères de performance du devis':
                d['curriculum_performance_criteria'] = value
            else:
                raise ValueError(f'Unknown key: {key}')

        return cls(**d)

    @staticmethod
    def to_empty_dict() -> dict:
        return {
            'titre': None,
            'numéro de leçon': None,
            'cours': None,
            'lieu': None,
            'date': None,
            'heure de début': None,
            'heure de fin': None,
            'cible d\'apprentissage': None,
            'matériel': None,
            'compétences du devis': None,
            'critères de performance du devis': None
        }


class LessonActivity(BaseModel):
    title: str
    objective: str
    duration: timedelta
    teaching_activity: str | list[str] = None
    learning_activity: str | list[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'LessonActivity':
        """
        Convert a dictionary with keys in French to a LessonActivity object.
        """
        d = {}
        for key, value in data.items():
            if key == 'titre':
                d['title'] = value
            elif key == 'objectif':
                d['objective'] = value
            elif key == 'durée':
                d['duration'] = value
            elif key == 'activité d\'enseignement':
                d['teaching_activity'] = value
            elif key == 'activité d\'apprentissage':
                d['learning_activity'] = value
            else:
                raise ValueError(f'Unknown key: {key}')
        return cls(**d)

    @staticmethod
    def to_empty_dict() -> dict:
        return {
            'titre': None,
            'objectif': None,
            'durée': None,
            'activité d\'enseignement': None,
            'activité d\'apprentissage': None
        }


class LessonIntro(BaseModel):
    duration: timedelta
    priming: str | None = None
    prior_knowledge_activation: str | list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict) -> 'LessonIntro':
        d = {}
        for key, value in data.items():
            if key == 'amorçage':
                d['priming'] = value
            elif key == 'activation des connaissances antérieures':
                d['prior_knowledge_activation'] = value
            elif key == 'durée':
                d['duration'] = value
            else:
                raise ValueError(f'Unknown key: {key}')
        return cls(**d)

    @staticmethod
    def to_empty_dict() -> dict:
        return {
            'durée': None,
            'amorçage': None,
            'activation des connaissances antérieures': None
        }


class LessonClosure(BaseModel):
    duration: timedelta
    for_next_time: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> 'LessonClosure':
        d = {}
        for key, value in data.items():
            if key == 'pour la prochaine fois':
                d['for_next_time'] = value
            elif key == 'durée':
                d['duration'] = value
            else:
                raise ValueError(f'Unknown key: {key}')
        return cls(**d)

    @staticmethod
    def to_empty_dict() -> dict:
        return {
            'durée': None,
            'pour la prochaine fois': None
        }


class LessonPlan(BaseModel):
    author: str = 'Vincent Archambault'
    lesson_info: LessonInfo
    lesson_intro: LessonIntro
    lesson_activities: list[LessonActivity]
    lesson_closure: LessonClosure

    @classmethod
    def from_yaml(cls, file_path: str) -> 'LessonPlan':
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'LessonPlan':
        d = {}
        for key, value in data.items():
            if key == 'informations générales':
                d["lesson_info"] = LessonInfo.from_dict(value)
            elif key == 'introduction':
                d["lesson_intro"] = LessonIntro.from_dict(value)
            elif key == 'activités':
                d["lesson_activities"] = [LessonActivity.from_dict(x) for x in value]
            elif key == 'conclusion':
                d["lesson_closure"] = LessonClosure.from_dict(value)
            elif key == 'auteur':
                d["author"] = value
            else:
                raise ValueError(f'Unknown key: {key}')
        return cls(**d)

    @staticmethod
    def to_empty_dict() -> dict:
        return {
            'auteur': None,
            'informations générales': LessonInfo.to_empty_dict(),
            'introduction': LessonIntro.to_empty_dict(),
            'activités': [LessonActivity.to_empty_dict()],
            'conclusion': LessonClosure.to_empty_dict()
        }

    def total_duration(self) -> timedelta:
        return (self.lesson_intro.duration
                + sum((activity.duration for activity in self.lesson_activities), start=timedelta())
                + self.lesson_closure.duration)


###############################################################################
# Latex formatting functions
###############################################################################
def duration_fmt(duration: timedelta, short: bool = False) -> str:
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    myminute = "min" if short else "minute"
    myhour = "h" if short else "heure"

    def pluralize(n: int, s: str) -> str:
        if short:
            return s
        return s if n <= 1 else s + 's'

    if hours == 0:
        return f'{minutes} {pluralize(minutes, myminute)}'

    if minutes == 0:
        return f'{hours} {pluralize(hours, myhour)}'

    return f'{hours} {pluralize(hours, myhour)} {minutes} {pluralize(minutes, myminute)}'


def duration_time_fmt(the_time: time | None, delta: timedelta) -> tuple[str, time | None]:
    str = f'{duration_fmt(delta)}'
    if the_time is None:
        return (str, None)
    end_time = (datetime.combine(date_type.today(), the_time) + delta).time()
    str = f'{str}, début à {the_time.strftime("%Hh%M")} et fin à {end_time.strftime("%Hh%M")}'
    return str, end_time


def lesson_info_to_dict(x: LessonInfo) -> dict:
    d = dict()
    if x.course:
        d['\\faBook{} Cours'] = x.course
    if x.lesson_number:
        d['{\\faHashtag} Numéro'] = x.lesson_number
    if x.date:
        d['{\\faCalendar*[regular]} Date'] = x.date.strftime('%-d %B %Y')
    if x.start_time and x.end_time:
        s = f'{x.start_time.strftime("%Hh%M")} - {x.end_time.strftime("%Hh%M")}'
        dur = datetime.combine(date_type.today(), x.end_time) - datetime.combine(date_type.today(),
                                                                                 x.start_time)
        s += f' ({duration_fmt(dur)})'
        d['{\\faClock[regular]} Heure'] = s
    if x.location:
        d['\\faLandmark{} Lieu'] = x.location
    if x.learning_objectives:
        d['\\faBullseye{} Objectifs'] = x.learning_objectives
    if x.curriculum_competencies:
        d['\\faToolbox{} Compétences du devis'] = x.curriculum_competencies
    if x.curriculum_performance_criteria:
        d['\\faUserCheck{} Critères de performance du devis'] = x.curriculum_performance_criteria
    if x.materials:
        d['\\faTv{} Matériel nécessaire'] = x.materials
    return d


def lesson_intro_to_dict(x: LessonIntro, plan: LessonPlan | None = None) -> dict:
    d = dict()
    if plan and plan.lesson_info.learning_objectives:
        d['\\faBullseye{} Objectifs de la leçon'] = plan.lesson_info.learning_objectives

    if plan:
        titles = [activity.title for activity in plan.lesson_activities]
        if titles:
            d['\\faList{} Plan de la leçon'] = titles

    if x.priming:
        d['\\faSurprise[regular]{} Amorçage'] = x.priming

    if x.prior_knowledge_activation:
        d['\\faUndo{} Activation des connaissances antérieures'] = x.prior_knowledge_activation
    return d


def lesson_closure_to_dict(x: LessonClosure, plan: LessonPlan | None = None) -> dict:
    d = dict()
    if plan and plan.lesson_info.learning_objectives:
        d['\\faList{} Résumé de la leçon'] = plan.lesson_info.learning_objectives

    if x.for_next_time:
        d['\\faCalendar*[regular]{} Pour la prochaine fois'] = x.for_next_time
    return d


def lesson_activity_to_dict(x: LessonActivity) -> dict:
    d = dict()
    d['\\faBullseye{} Objectif'] = x.objective
    if x.teaching_activity:
        d['\\faChalkboardTeacher{} Activité d\'enseignement'] = x.teaching_activity
    if x.learning_activity:
        d['\\faCalculator{} Activité d\'apprentissage'] = x.learning_activity
    return d


def dict_to_subsubsections(d: dict) -> str:
    tex = ''
    for key, value in d.items():
        tex += f'\\subsubsection*{{{key}}}\n'
        if isinstance(value, list):
            if len(value) == 1:
                tex += f'{value[0]}\n'
            else:
                tex += '\\begin{itemize}\n'
                for item in value:
                    tex += f'    \\item {item}\n'
                tex += '\\end{itemize}\n'
        else:
            tex += f'{value}\n'
    return tex


class LatexOptions(BaseModel):
    one_page_per_activity: bool = True


def generate_latex_content(lessonPlan: LessonPlan, opt: LatexOptions | None = None) -> str:
    if opt is None:
        opt = LatexOptions()

    # Set locale to French
    locale.setlocale(locale.LC_TIME, 'fr_CA.UTF-8')
    the_time = lessonPlan.lesson_info.start_time
    my_clearpage = '\\clearpage\n' if opt.one_page_per_activity else ''

    # Preamble
    tex_preamble = fr'''
% Compile document with LuaLaTeX
\documentclass[12pt]{{article}}

\usepackage{{fontspec}}
\usepackage{{unicode-math}}
\setromanfont{{Source Serif 4}}
\setsansfont{{Source Sans 3}}
\setmonofont{{Source Code Pro}}
\setmathfont{{Latin Modern Math}}
\setmainfont{{Source Sans 3}}
\usepackage[french]{{babel}}
\usepackage[letterpaper, margin=1in]{{geometry}}
\usepackage{{amsmath}}
\usepackage{{enumitem}}
\usepackage{{xltabular}}
\usepackage{{booktabs}}
\usepackage{{fontawesome5}}

\title{{Plan de leçon\\ {lessonPlan.lesson_info.lesson_title}}}
\author{{{lessonPlan.author}}}
\date{{}}

\begin{{document}}
'''

    # General information
    info_dict = lesson_info_to_dict(lessonPlan.lesson_info)
    tex_lesson_info = ""
    if info_dict:
        tex_lesson_info += '\\section*{Informations générales}\n'
        tex_lesson_info += '\\begin{description}\n'
        for key, value in info_dict.items():
            if isinstance(value, list):
                if len(value) == 1:
                    tex_lesson_info += f'\\item[{key}] {value[0]}\n'
                else:
                    tex_lesson_info += f'\\item[{key}]\n'
                    tex_lesson_info += '\\mbox{}\\newline\\leavevmode\\vspace{-3ex}'
                    tex_lesson_info += '\\begin{itemize}\n'
                    for item in value:
                        tex_lesson_info += f'    \\item {item}\n'
                    tex_lesson_info += '\\end{itemize}\n'
            else:
                tex_lesson_info += f'\\item[{key}] {value}\n'
        tex_lesson_info += '\\end{description}\n'

    # Lesson summary
    s = duration_fmt(lessonPlan.total_duration())
    tex_summary = f"{my_clearpage}\\section*{{Résumé de la leçon}}\n"
    tex_summary += "\\begin{description}\n"
    tex_summary += f"\\item[Durée totale] {s}\n"
    tex_summary += "\\end{description}\n"
    tex_summary += "\\renewcommand{\\arraystretch}{1.5}"
    tex_summary += fr'''
\newcolumntype{{Y}}{{>{{\raggedright\arraybackslash}}X}}
\newcolumntype{{Z}}{{>{{\raggedright\arraybackslash}}p{{2cm}}}}
\begin{{xltabular}}{{\textwidth}}{{>{{\hsize=.4\hsize}}Y >{{\hsize=.6\hsize}}Y Z}}
\toprule
\textbf{{Partie}} & \textbf{{Objectif}} & \textbf{{Durée}} \\ \midrule \endfirsthead
\toprule
\textbf{{Partie}} & \textbf{{Objectif}} & \textbf{{Durée}} \\ \midrule \endhead
Introduction & & {duration_fmt(lessonPlan.lesson_intro.duration, short=True)} \\
'''

    for activity in lessonPlan.lesson_activities:
        tex_summary += '{title} & {objective} & {duration} \\\\ \n'.format(
            title=activity.title,
            objective=activity.objective,
            duration=duration_fmt(activity.duration, short=True)
        )

    tex_summary += fr'''
Conclusion &  & {duration_fmt(lessonPlan.lesson_closure.duration, short=True)} \\
\bottomrule
\end{{xltabular}}
'''

    # Lesson intro
    intro_dict = lesson_intro_to_dict(lessonPlan.lesson_intro, lessonPlan)
    time_fmt, the_time = duration_time_fmt(the_time, lessonPlan.lesson_intro.duration)
    tex_intro = f'{my_clearpage}\\section{{Introduction}}\n'
    tex_intro += f'\\noindent {time_fmt}\n'
    if intro_dict:
        tex_intro += dict_to_subsubsections(intro_dict)

    # Lesson activities
    tex_activities = []
    for activity in lessonPlan.lesson_activities:
        act_dict = lesson_activity_to_dict(activity)
        time_fmt, the_time = duration_time_fmt(the_time, activity.duration)
        tex_act = f'{my_clearpage}\\section{{{activity.title}}}\n'
        tex_act += f'\\noindent {time_fmt}\n'
        if act_dict:
            tex_act += dict_to_subsubsections(act_dict)
        tex_activities.append(tex_act)
    tex_activities = '\n\n'.join(tex_activities)

    # Lesson closure
    closure_dict = lesson_closure_to_dict(lessonPlan.lesson_closure, lessonPlan)
    time_fmt, _ = duration_time_fmt(the_time, lessonPlan.lesson_closure.duration)
    tex_closure = f'{my_clearpage}\\section{{Conclusion}}\n'
    tex_closure += f'\\noindent {time_fmt}\n'
    if closure_dict:
        tex_closure += dict_to_subsubsections(closure_dict)

    # Putting it all together
    tex_content = [tex_preamble, '\\maketitle', tex_lesson_info, tex_summary, tex_intro,
                   tex_activities, tex_closure, '\\end{document}']
    tex_content = [x.strip() for x in tex_content]
    tex_content = [x for x in tex_content if x]
    return '\n\n'.join(tex_content)


def compile_latex(lesson_tex: str) -> None:
    output_dir = os.path.dirname(lesson_tex)
    subprocess.run(['latexmk', '-lualatex', '-output-directory=' + output_dir, lesson_tex],
                   check=True)
