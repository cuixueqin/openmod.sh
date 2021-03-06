if __name__ == '__main__':
    import openmod.sh.gui
    from oemof.db import config as cfg
    webport = cfg.get('openMod.sh R/W', 'webport')
    # to disaable login specify login_disabled = true in your config.ini
    openmod.sh.gui.app.run(host="0.0.0.0", port=int(webport), debug=True,
                           extra_files=['openmod/sh/templates/edit_scenario.html',
                                        'openmod/sh/static/plots.js'])
