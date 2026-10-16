#define _GNU_SOURCE
#include <assert.h>
#include <unistd.h>
#include "test_platform.h"
#include "../src/runtime_pad.c"

static int capture;
static Uint32 mouse_buttons;
static uint8_t camera_x, camera_y;
int bbgpu_overlay_captures_input(void) { return capture; }
uint32_t bbgpu_mouse_buttons(void) { return mouse_buttons; }
void bbgpu_camera_stick(uint8_t x, uint8_t y) { camera_x=x; camera_y=y; }
void bbgpu_mouse_take(double *dx, double *dy, int *up, int *down) { *dx=*dy=0; *up=*down=0; }
int bbgpu_mouse_captured(void) { return 0; }
void bbgpu_mouse_look_enable(int enabled) { (void)enabled; }
void bbgpu_mouse_capture(void) {}
int bbgpu_camera_look(float yaw, float pitch) { (void)yaw; (void)pitch; return 0; }
void bbgpu_filter_pad(uint32_t *buttons, const uint8_t *sticks) { (void)buttons; (void)sticks; }
void runtime_re_watch_tick(const void *pad_buffer, uint64_t reads) { (void)pad_buffer; (void)reads; }
uintptr_t runtime_libc_base;
uintptr_t runtime_lookup(const RuntimeExport *table, size_t count, const char *name) {
    (void)table; (void)count; (void)name;
    return 0;
}

static void inject(const char *path, const char *tokens) {
    FILE *f=fopen(path,"w");
    assert(f);
    fputs(tokens,f);
    fclose(f);
    usleep(25000);
}

int main(void) {
    char path[4096];
    int fd=bb_test_temp(path,sizeof(path),"bbport-pad-test");
    assert(fd>=0);
    close(fd);
    setenv("BB_PAD_FILE",path,1);
    /* bbport.ini controls: buttons moved, a trigger as a button and a button as a trigger. */
    char config[4096];
    int config_fd=bb_test_temp(config,sizeof(config),"bbport-pad-config");
    assert(config_fd>=0);
    const char controls[]="upscaler=fsr3\npad.cross=b\npad.circle=a\npad.r2=rightshoulder\n"
                          "pad.r1=righttrigger\nkey.cross=X, Space\npad.bogus=a\n"
                          "key.l3=Left Ctrl+C, Keypad +\n";
    assert(write(config_fd,controls,sizeof(controls)-1)==(ssize_t)(sizeof(controls)-1));
    close(config_fd);
    setenv("BB_CONFIG",config,1);
    setenv("SDL_VIDEODRIVER","dummy",1);
    /* Only the virtual test controller is a gamepad, whatever is plugged in. */
    SDL_SetHint(SDL_HINT_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT,"0x1d50/0x6189");
    assert(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMEPAD));
    /* The keyboard defaults: Escape the menu, R2 a Shift chord on the left button. */
    bind_defaults();
    assert(bindings[IN_OPTIONS].keys[0]==SDL_SCANCODE_ESCAPE && bindings[IN_OPTIONS].mods[0]<0);
    assert(bindings[IN_R2].keys[0]==MOUSE_KEY+SDL_BUTTON_LEFT && bindings[IN_R2].mods[0]==SDL_SCANCODE_LSHIFT);
    assert(bindings[IN_R1].keys[0]==MOUSE_KEY+SDL_BUTTON_LEFT && bindings[IN_R1].mods[0]<0);
    /* A chord on the keyboard: C alone is R3, Ctrl+C is L3 and not R3 too. */
    load_bindings();
    assert(bindings[IN_L3].key_count==2 && bindings[IN_L3].keys[0]==SDL_SCANCODE_C &&
           bindings[IN_L3].mods[0]==SDL_SCANCODE_LCTRL && bindings[IN_L3].keys[1]==SDL_SCANCODE_KP_PLUS &&
           bindings[IN_L3].mods[1]<0);
    {
        bool keys[SDL_SCANCODE_COUNT]={0};
        keys[SDL_SCANCODE_C]=true;
        assert(key_down(keys,IN_R3) && !key_down(keys,IN_L3));
        keys[SDL_SCANCODE_LCTRL]=true;
        assert(key_down(keys,IN_L3) && !key_down(keys,IN_R3));
    }
    assert(pad_init()==0 && pad_open(1,0,0,NULL)==1);
    PadData data;
    inject(path,"cross l3 touchpad_left");
    assert(pad_read_state(1,&data)==0);
    assert((data.buttons & (BTN_CROSS|BTN_L3|BTN_TOUCHPAD))==(BTN_CROSS|BTN_L3|BTN_TOUCHPAD));
    /* A new touch gets a new id (1..127), as from a DualShock 4: the game ignores id 0. */
    assert(data.touch_count==1 && data.touches[0].x==480 && data.touches[0].y==471 && data.touches[0].id==1);
    inject(path,"touchpad_right");
    assert(pad_read_state(1,&data)==0 && data.touch_count==1 && data.touches[0].x==1440);
    inject(path,"");
    assert(pad_read_state(1,&data)==0 && data.buttons==0 && data.touch_count==0);

    SDL_VirtualJoystickTouchpadDesc touch={.nfingers=2};
    SDL_VirtualJoystickDesc desc;
    SDL_INIT_INTERFACE(&desc);
    desc.type=SDL_JOYSTICK_TYPE_GAMEPAD;
    desc.naxes=SDL_GAMEPAD_AXIS_COUNT;
    desc.nbuttons=SDL_GAMEPAD_BUTTON_COUNT;
    desc.button_mask=(1u<<SDL_GAMEPAD_BUTTON_COUNT)-1;
    desc.axis_mask=(1u<<SDL_GAMEPAD_AXIS_COUNT)-1;
    desc.name="bbport test controller";
    desc.vendor_id=0x1d50;
    desc.product_id=0x6189;
    desc.ntouchpads=1;
    desc.touchpads=&touch;
    SDL_JoystickID id=SDL_AttachVirtualJoystick(&desc);
    assert(id!=0);
    SDL_Joystick *joystick=SDL_OpenJoystick(id);
    assert(joystick);
    assert(SDL_SetJoystickVirtualTouchpad(joystick,0,0,true,0.75f,0.5f,1.0f));
    assert(SDL_SetJoystickVirtualTouchpad(joystick,0,1,true,0.25f,1.0f,1.0f));
    assert(SDL_SetJoystickVirtualButton(joystick,SDL_GAMEPAD_BUTTON_TOUCHPAD,true));
    SDL_UpdateJoysticks();
    SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0);
    assert(gamepad && data.touch_count==2 && (data.buttons & BTN_TOUCHPAD));
    // The final native axes also drive mouse/controller ownership, including
    // vertical-only movement and neutralization while the port menu is open.
    assert(SDL_SetJoystickVirtualAxis(joystick,SDL_GAMEPAD_AXIS_RIGHTY,-32768));
    SDL_UpdateJoysticks(); SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0 && data.right_y==0);
    assert(camera_x==data.right_x && camera_y==0);
    assert(SDL_SetJoystickVirtualAxis(joystick,SDL_GAMEPAD_AXIS_RIGHTX,32767));
    SDL_UpdateJoysticks(); SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0 && camera_x==255 && camera_y==0);
    assert(SDL_SetJoystickVirtualAxis(joystick,SDL_GAMEPAD_AXIS_RIGHTX,0));
    assert(SDL_SetJoystickVirtualAxis(joystick,SDL_GAMEPAD_AXIS_RIGHTY,0));
    SDL_UpdateJoysticks(); SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0 && camera_x==128 && camera_y==128);
    assert(data.touches[0].x==1439 && data.touches[0].y==471 && data.touches[0].id==2);
    assert(data.touches[1].x==480 && data.touches[1].y==942 && data.touches[1].id==3);
    capture=1;
    assert(pad_read_state(1,&data)==0 && data.touch_count==0 && data.buttons==0);
    assert(camera_x==128 && camera_y==128);
    capture=0;
    assert(SDL_SetJoystickVirtualTouchpad(joystick,0,0,false,0,0,0));
    assert(SDL_SetJoystickVirtualTouchpad(joystick,0,1,false,0,0,0));
    SDL_UpdateJoysticks();
    SDL_UpdateGamepads();
    // A touchpad/button still held when the menu closes must not become a new gesture.
    assert(pad_read_state(1,&data)==0 && data.touch_count==0 && data.buttons==0);
    assert(SDL_SetJoystickVirtualButton(joystick,SDL_GAMEPAD_BUTTON_TOUCHPAD,false));
    SDL_UpdateJoysticks();
    SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0 && data.buttons==0 && data.touch_count==0);
    assert(SDL_SetJoystickVirtualButton(joystick,SDL_GAMEPAD_BUTTON_EAST,true));
    assert(SDL_SetJoystickVirtualButton(joystick,SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER,true));
    assert(SDL_SetJoystickVirtualAxis(joystick,SDL_GAMEPAD_AXIS_RIGHT_TRIGGER,32767));
    SDL_UpdateJoysticks();
    SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0);
    assert(data.buttons==(BTN_CROSS|BTN_R2|BTN_R1) && data.r2==255);
    assert(bindings[IN_CROSS].key_count==2 && bindings[IN_CROSS].keys[0]==SDL_SCANCODE_X &&
           bindings[IN_CROSS].keys[1]==SDL_SCANCODE_SPACE);
    /* Capture-helper names round-trip through the actual INI parser and pad ABI. */
    FILE *mouse_config=fopen(config,"w");
    assert(mouse_config);
    fputs("key.cross=Space, Mouse Left\nkey.r1=Mouse X1\nkey.r2=Mouse Right\n"
          "key.square=Mouse Middle\nkey.circle=Mouse X2\nkey.up=Mouse Wheel Up\n"
          "key.down=Mouse Wheel Down\nkey.left=Mouse Wheel Left\nkey.right=Mouse Wheel Right\n"
          "key.triangle=Comma\nkey.move_up=Mouse Left\n",mouse_config);
    fclose(mouse_config);
    load_bindings();
    assert(bindings[IN_CROSS].key_count==1 && bindings[IN_CROSS].mouse_count==1);
    bool keyboard[SDL_SCANCODE_COUNT]={0};
    PadData mapped={.left_x=128,.left_y=128,.right_x=128,.right_y=128};
    apply_keyboard(&mapped,keyboard,SDL_BUTTON_LMASK|SDL_BUTTON_MMASK|SDL_BUTTON_RMASK|
                   SDL_BUTTON_X1MASK|SDL_BUTTON_X2MASK|BB_WHEEL_UP|BB_WHEEL_RIGHT);
    assert(mapped.buttons==(BTN_CROSS|BTN_SQUARE|BTN_CIRCLE|BTN_R1|BTN_R2|BTN_UP|BTN_RIGHT));
    assert(mapped.r2==255 && mapped.left_y==0);
    keyboard[SDL_SCANCODE_COMMA]=true;
    mapped=(PadData){0};
    apply_keyboard(&mapped,keyboard,0);
    assert(mapped.buttons==BTN_TRIANGLE);
    keyboard[SDL_SCANCODE_COMMA]=false;
    mapped=(PadData){0};
    apply_keyboard(&mapped,keyboard,BB_WHEEL_DOWN|BB_WHEEL_LEFT);
    assert(mapped.buttons==(BTN_DOWN|BTN_LEFT));
    mapped=(PadData){0};
    apply_keyboard(&mapped,keyboard,0);
    assert(mapped.buttons==0);
    mouse_buttons=SDL_BUTTON_RMASK;
    capture=1;
    assert(pad_read_state(1,&data)==0 && data.buttons==0 && data.r2==0);
    capture=0;
    mouse_buttons=0;
    SDL_CloseJoystick(joystick);
    if (gamepad) SDL_CloseGamepad(gamepad);
    gamepad=NULL;
    assert(SDL_DetachVirtualJoystick(id));
    SDL_Quit();
    unlink(path);
    unlink(config);
    /* Mouse: names, the look stick's speed-to-deflection at two frame rates, the wheel's presses. */
    assert(key_from_name("Mouse Left")==MOUSE_KEY+SDL_BUTTON_LEFT && key_from_name("wheel down")==MOUSE_WHEEL_DOWN);
    for (int rate=60;rate<=240;rate*=4) {
        PadData m; memset(&m,0,sizeof m);
        look_x=look_y=0; look_last_us=1;
        const uint64_t step=1000000/rate;
        for (int i=1;i<=rate;++i) { /* 500 pixels/s to the right for a second */
            m.right_x=m.right_y=128;
            apply_mouse_look(&m,500.0/rate,0,1+i*step,1);
        }
        assert(m.right_x>=128+16+50 && m.right_x<=128+16+62 && m.right_y==128);
        m.right_x=128;
        apply_mouse_look(&m,0,0,1+(rate+60)*step,1); /* still: back to the pad's stick */
        for (int i=0;i<20;++i) apply_mouse_look(&m,0,0,1+(rate+61+i)*step,1);
        assert(m.right_x==128);
    }
    mouse_wheel_step(1000000,0,2);
    assert(wheel_phase[1]==1 && mouse_key_down(MOUSE_WHEEL_DOWN));
    mouse_wheel_step(1070000,0,0);
    assert(!mouse_key_down(MOUSE_WHEEL_DOWN));
    mouse_wheel_step(1140000,0,0);
    assert(mouse_key_down(MOUSE_WHEEL_DOWN) && wheel_pending[1]==0);
    puts("PASS: pad ABI, debug camera chord, left/right clicks, SDL touch coordinates, overlay capture, controls, mouse");
}
