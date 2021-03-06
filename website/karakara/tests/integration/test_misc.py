
def test_home(app):
    """
    Main Menu
    """
    response = app.get('/')
    assert response.status_code == 200
    assert 'html' in response.content_type
    for text in ['KaraKara', 'jquery-1.', 'jquery.mobile', 'Feedback', 'Explore']:
        assert text in response.text
    
def test_admin_toggle(app):
    """
    Swich to admin mode
    check main menu for admin options
    """
    assert not app.get('/?format=json').json['identity']['admin']
    
    response = app.get('/admin')
    assert 'admin' in response.text
    response = app.get('/')
    for text in ['Exit Admin Mode']:
        assert text in response.text
    
    assert app.get('/?format=json').json['identity']['admin']

    response = app.get('/admin')
