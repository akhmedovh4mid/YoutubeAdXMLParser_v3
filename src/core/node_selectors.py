class Selectors:
    class Main:
        main_node = {
            "className": "android.view.ViewGroup",
            "resourceId": "com.google.android.youtube:id/next_gen_watch_layout_no_player_fragment_container"
        }
        video_player_node = {
            "className": "android.widget.FrameLayout",
            "resourceId": "com.google.android.youtube:id/watch_player"
        }
        time_bar_node = {
            "className": "android.view.ViewGroup",
            "resourceId": "com.google.android.youtube:id/watch_while_time_bar_view"
        }
        engagement_panel_node = {
            "className": "android.view.ViewGroup",
            "resourceId": "com.google.android.youtube:id/engagement_panel_wrapper"
        }
        video_metadata_node = {
            "className": "android.widget.FrameLayout",
            "resourceId": "com.google.android.youtube:id/video_metadata_layout"
        }

    class Player:
        control_button = {
            "className": "android.widget.ImageView",
            "resourceId": "com.google.android.youtube:id/player_control_play_pause_replay_button"
        }
        progress_bar = {
            "className": "android.widget.ProgressBar",
            "resourceId": "com.google.android.youtube:id/player_loading_view_thin"
        }

    class Ad:
        drag_handle_button = {
            "className": "android.widget.ImageView",
            "resourceId": "com.google.android.youtube:id/arrow_drag_handle"
        }
        header_panel_node = {
            "className": "android.widget.FrameLayout",
            "resourceId": "com.google.android.youtube:id/panel_header"
        }
        close_ad_button = {
            "className": "android.widget.Button",
            "description": "Close ad panel"
        }
        
    class Content:
        watch_list_node = {
            "className": "android.support.v7.widget.RecyclerView",
            "resourceId": "com.google.android.youtube:id/watch_list"
        }
        relative_container_node = {
            "className": "android.widget.LinearLayout",
            "resourceId": "com.google.android.youtube:id/related_chip_cloud_container"
        }
        ad_block_node = {
            "className": "android.view.ViewGroup",
            "descriptionStartsWith": "Sponsored"
        }

    class Chrome:
        toolbar_node = {
            "className": "android.widget.FrameLayout",
            "resourceId": "com.android.chrome:id/toolbar"
        }
        action_button = {
            "className": "android.widget.LinearLayout",
            "resourceId": "com.android.chrome:id/action_buttons"
        }
        content_preview_text = {
            "className": "android.widget.TextView",
            "resourceId": "android:id/content_preview_text"
        }
        
    class Class:
        image_view = {
            "className": "android.widget.ImageView"
        }
        view_group = {
            "className": "android.view.ViewGroup"
        }
        button = {
            "className": "android.widget.Button"
        }
        text_view = {
            "className": "android.widget.TextView"
        }
        view = {
            "className": "android.view.View"
        }
        relative_layout = {
            "className": "android.widget.RelativeLayout"
        }
