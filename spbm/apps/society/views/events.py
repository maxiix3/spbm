from django.contrib.auth.decorators import login_required
from django.forms.formsets import all_valid
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from extra_views import CreateWithInlinesView, InlineFormSet, UpdateWithInlinesView

from spbm.helpers.auth import user_allowed_society, user_society
from spbm.helpers.mixins import LoginAndPermissionRequiredMixin
from ..forms.events import make_shift_base
from ..models import Society, Event, Shift


@login_required
def index(request, society_name=None):
    society = request.user.spfuser.society if society_name is None \
        else get_object_or_404(Society, shortname=society_name)

    # TODO: possibly remove this, while at the same time reworking the entire thought of multi-society editing
    # it is, by far, more important to have multi-society workers
    if not user_allowed_society(request.user, society):
        return render(request, "errors/unauthorized.jinja")

    events = Event.objects.filter(society=society)
    processed = events.values('processed').distinct().extra(select={'processed_is_null': 'processed IS NULL'},
                                                            order_by=['-processed_is_null', '-processed'])
    events_by_date = {}
    for event in processed:
        events_by_date[event['processed']] = events.filter(processed=event['processed']).order_by('-date')

    return render(request, "events/index.jinja",
                  {'processed': processed, 'events': events_by_date, 'cur_page': 'events'})


class ShiftInlineForm(InlineFormSet):
    model = Shift
    exclude = ['norlonn_report']
    can_delete = False

    def get_form_class(self):
        return make_shift_base(user_society(self.request))

    def get_factory_kwargs(self):
        kwargs = super(ShiftInlineForm, self).get_factory_kwargs()
        kwargs.update({
            'min_num': 1,
        })
        return kwargs


class EventCreateView(LoginAndPermissionRequiredMixin, CreateWithInlinesView):
    template_name = "events/add.jinja"
    permission_required = 'society.add_event'
    permission_denied_message = _("You are not allowed to create events due to lacking permissions.")
    model = Event
    fields = ['name', 'date']
    inlines = [ShiftInlineForm, ]

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.society = user_society(request)
            form_validated = True
        else:
            self.object = None
            form_validated = False

        inlines = self.construct_inlines()

        if all_valid(inlines) and form_validated:
            return self.forms_valid(form, inlines)
        return self.forms_invalid(form, inlines)


class EventUpdateView(LoginAndPermissionRequiredMixin, UpdateWithInlinesView):
    template_name = "events/add.jinja"
    permission_required = 'society.change_event'
    permission_denied_message = _("You are not allowed to edit events due to lacking permissions.")
    model = Event
    fields = ['name', 'date']
    inlines = [ShiftInlineForm, ]
