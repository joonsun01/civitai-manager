import os
import datetime
import gradio as gr
import modules.scripts as scripts

from modules import shared
from modules import script_callbacks

from scripts.civitai_manager_libs import setting
from scripts.civitai_manager_libs import model_action
from scripts.civitai_manager_libs import classification_action
from scripts.civitai_manager_libs import civitai_shortcut_action

def on_civitai_tabs_select(evt: gr.SelectData):
    if evt.index == 0:
        current_time = datetime.datetime.now() 
        return current_time,gr.update(visible=False)
    elif evt.index == 1:
        current_time = datetime.datetime.now() 
        return gr.update(visible=False),current_time
            
    return gr.update(visible=False),gr.update(visible=False)
                   
def civitai_shortcut_ui():    
    with gr.Tabs(elem_id="civitai_shortcut_tabs_container") as civitai_tabs:
        with gr.TabItem("Civitai Shortcut" , id="Shortcut"):
            with gr.Row(visible=False):
          
                # SC 리스트틑 갱신하게 된다.
                refresh_shortcut = gr.Textbox()              
                refresh_classification = gr.Textbox()
                
            with gr.Row():
                civitai_shortcut_action.on_ui(refresh_shortcut)
     
        with gr.TabItem("Manage" , id="Manage"):
            with gr.Tabs() as civitai_manage_tabs:        
                with gr.TabItem("Classification"):
                    with gr.Row():
                        classification_action.on_ui(refresh_classification)
    
    # civitai tab start
    civitai_tabs.select(
        fn=on_civitai_tabs_select,
        inputs=None,
        outputs=[refresh_shortcut,refresh_classification]
    )
            
def init_civitai_shortcut():
   
    setting.root_path = os.getcwd()
    
    if shared.cmd_opts.embeddings_dir:
        setting.model_folders[setting.model_types['textualinversion']] = shared.cmd_opts.embeddings_dir

    if shared.cmd_opts.hypernetwork_dir :
        setting.model_folders[setting.model_types['hypernetwork']] = shared.cmd_opts.hypernetwork_dir

    if shared.cmd_opts.ckpt_dir:
        setting.model_folders[setting.model_types['checkpoint']] = shared.cmd_opts.ckpt_dir

    if shared.cmd_opts.lora_dir:
        setting.model_folders[setting.model_types['lora']] = shared.cmd_opts.lora_dir
        setting.model_folders[setting.model_types['locon']] = shared.cmd_opts.lora_dir
    
    setting.shortcut = os.path.join(scripts.basedir(),setting.shortcut)
    setting.shortcut_classification = os.path.join(scripts.basedir(),setting.shortcut_classification)
    setting.shortcut_thumbnail_folder = os.path.join(scripts.basedir(),setting.shortcut_thumbnail_folder)
    setting.shortcut_save_folder = os.path.join(scripts.basedir(),setting.shortcut_save_folder)
    setting.shortcut_info_folder = os.path.join(scripts.basedir(),setting.shortcut_info_folder)
    
    # 소유한 모델을 스캔하여 저장한다.
    model_action.Load_Downloaded_Models()
               
# init
init_civitai_shortcut()

def on_ui_tabs():
    # with gr.Blocks(analytics_enabled=False) as civitai_shortcut:
    with gr.Blocks() as civitai_shortcut:
        civitai_shortcut_ui()
    
    return (civitai_shortcut, "Civitai Shortcut", "civitai_shortcut"),


script_callbacks.on_ui_tabs(on_ui_tabs)
