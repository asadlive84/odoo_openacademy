# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions
from odoo.exceptions import ValidationError

# class openacademy(models.Model):
#     _name = 'openacademy.openacademy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100




class Course(models.Model):
    _name='openacademy.course'

    name=fields.Char(string="Title", required=True)
    description=fields.Text()

    responsible_id=fields.Many2one('res.users', ondelete='set null', string='Responsible', index=True)

    session_ids=fields.One2many('openacademy.session','course_id', string="Sessions")


    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)


    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]





class Session(models.Model):

    _name='openacademy.session'

    name=fields.Char(required=True)
    start_date=fields.Date(default=fields.Date.today)

    duration=fields.Float(digits=(6,2), help="Durations in Days")
    seats=fields.Integer(string="Number of seats")

    
    instructor_id=fields.Many2one('res.partner', string='Instructor', domain=['|',('instructor','=','True'), ('category_id.name','ilike',"Teacher")])

    active=fields.Boolean(default=True)


    course_id=fields.Many2one('openacademy.course', ondelete="cascade", string="Course", required=True)

    attendee_ids=fields.Many2many('res.partner',string="Attendee")

    taken_seats=fields.Float(string="Taken Seats", compute="_taken_seats")


    @api.depends("seats","attendee_ids")
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats=0.0
            else:
                r.taken_seats=100.0*len(r.attendee_ids)/r.seats

    

    @api.constrains('instructor_id','attendee_ids')
    def _check_instructor_not_in_attendee(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")
