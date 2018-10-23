# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import fields, models,api
import pandas as pd


class examEvaluation(models.AbstractModel):
    _name = 'report.education_exam.report_merit_list'

    def get_merit_list(self,object):
        list=[]
        stu=[]
        scor=[]
        exa=[]
        merit_class=[]
        merit_section=[]
        for exam in object.exams:
            student_list = self.env['education.class.history'].search([('level.id', '=', object.level.id)])
            for student in student_list:
                total=0
                mark_line = self.env['results.subject.line'].search(
                    [('student_id', '=', student.id), ('exam_id', '=', exam.id)])
                for line in mark_line:
                    total=total+line.mark_scored
                stu.append(student)
                exa.append(exam)
                scor.append(total)
                merit_class.append(0)
                merit_section.append(0)
            data={'student':stu,"exam":exa,'Score':scor,'merit_class':merit_class,'merit_section':merit_section}
        df= pd.DataFrame(data)
        result = df.sort_values(by=['Score'], ascending=False)
        result=result.reset_index(drop=True)
        for i in range(0,len(result)):
            result.at[i,'merit_class']=i+1
            i=i+1
        print(result)
        return result





    def get_sections(self,object):
        sections=[]

        if object.section:
            return object.section
        elif object.level:
            section=self.env['education.class.division'].search([('class_id','=',object.level.id),('academic_year_id','=',object.academic_year.id)])
            return section
    def get_exams(self, objects):
        exams = []
        for exam in objects.exams:
           exams.extend(exam)

        return exams

    def get_students(self,objects):

        student=[]
        student_list=self.env['education.class.history'].search([('class_id.id', '=', objects.id)])
        for stu in student_list:
            student.extend(stu.student_id)
        return student
    def get_subjects(self, section,obj):
        subjs=self.env['education.syllabus'].search([('class_id','=',section.class_id.id),('academic_year','=',obj.academic_year.id)])

        return subjs
    def get_marks(self,subject,student,exam):
        marks=[]
        mark_line=self.env['results.subject.line'].search([('student_id','=',student.id),('exam_id','=',exam.id),('subject_id','=',subject.id)])
        if len(mark_line)==0:
            if subject.tut_mark >0:
                marks.append('0')
            if subject.subj_mark >0:
                marks.append('0')
            if subject.obj_mark >0:
                marks.append('0')
            if subject.prac_mark >0:
                marks.append('0')
        else:
            if mark_line.subject_id.tut_mark>0:
                marks.append(mark_line.tut_mark)
            elif  mark_line.subject_id.subj_mark>0:
                marks.append(mark_line.subj_mark)
            elif mark_line.subject_id.obj_mark > 0:
                marks.append(mark_line.obj_mark)
            elif  mark_line.subject_id.prac_mark>0:
                marks.append(mark_line.prac_mark)
        return marks








    def get_gradings(self,obj):
        grading=self.env['education.result.grading'].search([('id','>','0')],order='min_per desc',)
        grades=[]
        for grade in grading:
            grades.extend(grade)
        return grades


    def get_date(self, date):
        date1 = datetime.strptime(date, "%Y-%m-%d")
        return str(date1.month) + ' / ' + str(date1.year)

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['academic.transcript'].browse(docids)

        return {
            'doc_model': 'education.exam.results',
            'docs': docs,
            'time': time,
            'get_students': self.get_students,
            'get_exams': self.get_exams,
            'get_subjects': self.get_subjects,
            'get_gradings':self.get_gradings,
            'get_date': self.get_date,
            'get_sections': self.get_sections,
            'get_marks': self.get_marks,
            'get_merit_list': self.get_merit_list,
        }
