from pyglet.gl import *
from math import floor
from blocks import *

class InventorySelector(object):
    def __init__(self, width, height, player, model):
        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.OrderedGroup(1)
        self.amount_labels_group = pyglet.graphics.OrderedGroup(2)
        self.amount_labels = []
        self.model = model
        self.player = player
        self.max_items = 27
        self.current_index = 1
        self.icon_size = self.model.group.texture.width / 8 #4

        image = pyglet.image.load('inventory.png')
        frame_size = image.height * 3 / 4
        self.frame = pyglet.sprite.Sprite(image.get_region(0, image.height - frame_size, image.width, frame_size), batch=self.batch, group=pyglet.graphics.OrderedGroup(0))
        self.active = pyglet.sprite.Sprite(image.get_region(0, 0, image.height / 4, image.height / 4), batch=self.batch, group=pyglet.graphics.OrderedGroup(2))
        self.active.opacity = 0
        self.set_position(width, height)

    def change_index(self, change):
        self.set_index(self.current_index + change)

    def set_index(self, index):
        index = int(index)
        if self.current_index == index:
            return
        self.current_index = index
        if self.current_index >= self.max_items:
            self.current_index = 0
        elif self.current_index < 0:
            self.current_index = self.max_items - 1;
        self.update_current()

    def update_items(self):
        self.icons = []
        for amount_label in self.amount_labels:
            amount_label.delete()
        self.amount_labels = []
        x = self.frame.x + 3
        items = self.player.inventory.get_items()
        items = items[:self.max_items]
        for i, item in enumerate(items):
            if not item:
                x += (self.icon_size * 0.5) + 3
                if x - self.frame.x - 3 >= self.frame.width:
                    x = self.frame.x + 3
                continue
            block = BLOCKS_DIR[item.type]
            block_icon = self.model.group.texture.get_region(int(block.side_texture[0] * 8) * self.icon_size, int(block.side_texture[1] * 8) * self.icon_size, self.icon_size, self.icon_size)
            icon = pyglet.sprite.Sprite(block_icon, batch=self.batch, group=self.group)
            icon.scale = 0.5
            icon.x = x
            icon.y = self.frame.y + floor(i / 9) * 6 + floor(i / 9) * self.icon_size * 0.5 + 3
            item.inventory_x = icon.x
            item.inventory_y = icon.y
            x += (self.icon_size * 0.5) + 3
            if x - self.frame.x >= self.frame.width:
                x = self.frame.x + 3
            amount_label = pyglet.text.Label(str(item.amount), font_name='Arial', font_size=9, 
                x=icon.x + 3, y=icon.y, anchor_x='left', anchor_y='bottom', 
                color=(block.amount_label_color), batch=self.batch, group=self.amount_labels_group)
            self.amount_labels.append(amount_label)
            self.icons.append(icon)
        
    def update_current(self):
        self.active.x = self.frame.x + ((self.current_index % 9) * self.icon_size * 0.5) + (self.current_index % 9) * 3
        self.active.y = self.frame.y + floor(self.current_index / 9) * self.icon_size * 0.5 + floor(self.current_index / 9) * 6
        
    def set_position(self, width, height):
        self.frame.x = (width - self.frame.width) / 2
        self.frame.y = self.icon_size + 20 # 20 is padding
        self.update_current()
        self.update_items()

    def get_current_block(self):
        item = self.player.inventory.at(self.current_index)
        if item:
            item_id = item.type
            self.player.inventory.remove_by_index(self.current_index)
            self.update_items()
            if item_id >= ITEM_ID_MIN:
                return ITEMS_DIR[item_id]
            else:
                return BLOCKS_DIR[item_id]
        return False

    def get_current_block_item_and_amount(self):
        item = self.player.inventory.at(self.current_index)
        if item:
            amount = item.amount
            self.player.inventory.remove_by_index(self.current_index, quantity=item.amount)
            return (item, amount)
        return False

    def toggle_active_frame_visibility(self):
        self.active.opacity = 0 if self.active.opacity == 255 else 255

    def mouse_coords_to_index(self, x, y):
        for i, item in enumerate(self.player.inventory.get_items()):
            if item and item.inventory_x and item.inventory_y:
                if x >= item.inventory_x and y >= item.inventory_y and \
                x <= item.inventory_x + self.icon_size * 0.5 and y <= item.inventory_y + self.icon_size * 0.5:
                    return i
        return -1

    def on_mouse_press(self, x, y, button):
        index = self.mouse_coords_to_index(x, y)
        # previous implentation of this function was doing something strange
        # and caused item loss
        if index == -1:
            pass
        elif index == self.current_index:
            current_block = self.get_current_block_item_and_amount()
            if current_block:
                if not self.player.quick_slots.add_item(
                        current_block[0].id,
                        quantity=current_block[1]):
                    self.player.inventory.add_item(current_block[0].id,
                                                   quantity=current_block[
                                                       1])
        else:
            self.current_index = index
            self.update_current()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass # TODO: Allow dragging & dropping items