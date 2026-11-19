
from datetime import datetime, timedelta
from encryption import Encryption

from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from app.models import User
from app import db
from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_stats.vk_stats import VKStats


smm_bp = Blueprint('smm', __name__)


@smm_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')


@smm_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        vk_api_id = request.form.get('vk_api_id', '').strip()
        vk_group_id = request.form.get('vk_group_id', '').strip()
        openai_api_key = request.form.get('openai_api_key', '').strip()

        if not vk_api_id or not vk_group_id:
            flash('Заполните оба поля ВКонтакте.', 'danger')
        else:
            user.vk_api_id = vk_api_id
            user.vk_group_id = vk_group_id

            if openai_api_key:
                encryption = Encryption()
                user.openai_api_key = encryption.encrypt(openai_api_key)

            db.session.commit()

            flash('Настройки сохранены!', 'success')
            return redirect(url_for('smm.settings'))

    return render_template('settings.html', user=user)


@smm_bp.route('/post-generator', methods=['GET', 'POST'])

def post_generator():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        tone = request.form['tone']
        topic = request.form['topic']
        generate_image = 'generate_image' in request.form
        auto_post = 'auto_post' in request.form

        if not user.openai_api_key:
            flash(
                'Сначала добавьте OpenAI API Key в настройках.',
                'danger'
            )
            return redirect(url_for('smm.settings'))

        try:
            encryption = Encryption()
            decrypted_api_key = encryption.decrypt(user.openai_api_key)

            post_gen = PostGenerator(decrypted_api_key, tone, topic)
            post_content = post_gen.generate_post()

            image_url = None
            image_path = None

            if generate_image:
                image_gen = ImageGenerator(decrypted_api_key)
                image_prompt = post_gen.generate_post_image_description()
                image_path = image_gen.generate_image(image_prompt)

                filename = image_path.replace("\\", "/").split("/")[-1]
                image_url = url_for('static', filename=f'generated/{filename}')

            if auto_post:
                vk_publisher = VKPublisher(user.vk_api_id, user.vk_group_id)
                vk_publisher.publish_post(post_content, image_path)
                flash(
                    'Публикация успешно размещена во ВКонтакте!',
                    'success'
                )

            return render_template(
                'post_generator.html',
                post_content=post_content,
                image_url=image_url
            )

        except Exception as e:
            flash(str(e), 'danger')
            return render_template('post_generator.html')

    return render_template('post_generator.html')


@smm_bp.route('/vk-stats', methods=['GET'])
def vk_stats():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    vk_stats = VKStats(user.vk_api_id, user.vk_group_id)
    followers_count = vk_stats.get_followers()
    posts_stats = vk_stats.get_posts_stats()

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    community_stats = vk_stats.get_stats(start_date, end_date)

    stats = {
        "Followers": followers_count,
        "Reach": community_stats.get('reach', {}).get('reach', 0),
        "Reach of subscribers": community_stats.get('reach', {}).get('reach_subscribers', 0),
        "Visitors": community_stats.get('visitors', {}).get('visitors', 0),
        "Views": community_stats.get('visitors', {}).get('views', 0),
        "Comments": community_stats.get('activity', {}).get('comments', 0),
        "Likes": posts_stats.get('likes', 0),
        "Reposts": posts_stats.get('reposts', 0)
    }

    return render_template('vk_stats.html', stats=stats)
