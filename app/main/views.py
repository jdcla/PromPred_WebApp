from datetime import datetime
from flask import render_template, flash, redirect, url_for, session, request, current_app
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from . import main
from .forms import PromLibForm, PromPlanForm, PromSeqForm, PostForm
from .. import db
from ..models import User, Promoter_library, Plan, Sequence, Post, Permission

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"



@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    lib_form = PromLibForm()
    plan_form = PromPlanForm()
    seq_form = PromSeqForm()
    post_form = PostForm()
    libraries = Promoter_library.query.filter_by(creator_lib=current_user._get_current_object())
    ref_libraries = Promoter_library.query.filter_by(is_reference=True)
    ref_sequences = Sequence.query.join(Promoter_library).filter(Promoter_library.is_reference==1)
    ref_dict = { ref_lib.name : [ref_seq.name for ref_seq in ref_sequences if ref_seq.library == ref_lib.id] for ref_lib in ref_libraries}
    plans = Plan.query.filter_by(creator_plan=current_user._get_current_object())
    if lib_form.submit_lib.data and lib_form.validate_on_submit():
        library = Promoter_library(name=lib_form.name_lib.data, creator_lib=current_user._get_current_object())
        db.session.add(library)
        db.session.commit()
        flash('Promoter library created!')

    if plan_form.submit_plan.data and plan_form.validate_on_submit():
        plan = Plan(name=plan_form.name_plan.data, body=plan_form.plan.data, creator_plan=current_user._get_current_object())
        db.session.add(plan)
        db.session.commit()
        flash('Blueprint created!')

    if seq_form.submit_seq.data and seq_form.validate_on_submit():
        plan = Plan(name=plan_form.name_plan.data, plan=plan_form.plan.data,
                    creator_seq=current_user._get_current_object())

        db.session.add(plan)
        db.session.commit()
        flash('Sequence submitted!')

    if current_user.can(Permission.WRITE_POSTS) and post_form.submit_post.data and post_form.validate_on_submit():
        post = Post(body=post_form.body.data, title=post_form.title.data, creator_post=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['PROMPRED_POSTS_PER_PAGE'],
                                                                     error_out=False)
    posts = pagination.items
    return render_template('index.html', lib_form=lib_form, plan_form=plan_form, seq_form=seq_form, post_form=post_form,
                           libraries=libraries, ref_libraries=ref_libraries, ref_sequences=ref_sequences, plans=plans,
                           ref_dict=ref_dict, posts=posts, pagination=pagination, current_time=datetime.utcnow())


@main.route('/library', methods=['GET', 'POST'])
@login_required
def library():
    libraries = Promoter_library.query.filter_by(creator_lib=current_user._get_current_object())
    lib_form= PromLibForm()
    if lib_form.submit_lib.data and lib_form.validate_on_submit():
        library = Promoter_library(name=lib_form.name_lib.data, creator_lib=current_user._get_current_object())
        db.session.add(library)
        db.session.commit()
        #create_promoter_lib.delay(current_user._get_current_object(),library)
        flash('Promoter library created!')

    return render_template('library.html', lib_form=lib_form, libraries=libraries)


@main.route('/library/delete/<lib_id>')
@login_required
def delete_library(lib_id):
    library = Promoter_library.query.filter_by(id=lib_id, creator_lib=current_user._get_current_object()).first()
    sequences = Sequence.query.filter_by(library_seq=library, creator_seq=current_user._get_current_object())
    for sequence in sequences:
        db.session.delete(sequence)
    db.session.delete(library)
    db.session.commit()
    return redirect(url_for('main.library'))

@main.route('/library/<lib_id>')
@login_required
def sequences(lib_id):
    library = Promoter_library.query.filter_by(id=lib_id, creator_lib=current_user._get_current_object()).first()
    sequences = Sequence.query.filter_by(library_seq=library, creator_seq=current_user._get_current_object())
    return render_template('promoters.html', library = library, sequences = sequences)

@main.route('/blueprint', methods=['GET', 'POST'])
@login_required
def blueprint():
    plans = Plan.query.filter_by(creator_plan=current_user._get_current_object())
    plan_form= PromPlanForm()
    if plan_form.submit_plan.data and plan_form.validate_on_submit():
        plan = Plan(name=plan_form.name_plan.data, body=plan_form.plan.data, creator_plan=current_user._get_current_object())
        db.session.add(plan)
        db.session.commit()

        flash('Promoter Blueprint created!')

    return render_template('blueprint.html', plan_form=plan_form, plans=plans)


@main.route('/blueprint/delete/<plan_id>')
@login_required
def delete_plan(plan_id):
    plan = Plan.query.filter_by(id=plan_id, creator_plan=current_user._get_current_object()).first()
    db.session.delete(plan)
    db.session.commit()
    return redirect(url_for('main.blueprint'))


@main.route('/about')
def about():
    return render_template('about.html')