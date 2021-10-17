import json
from fastapi import FastAPI, HTTPException

with open("menu.json", "r") as read_file:
      data = json.load(read_file)

app = FastAPI()

# Read Menu
@app.get('/menu/{item_id}')
async def read_menu(item_id: int):
      for menu_item in data['menu']:
            if menu_item['id'] == item_id:
                  return menu_item

      raise HTTPException(
            status_code=404, detail=f'Item not found'
      )

# Update Menu
@app.put('/menu/{item_id}')
async def update_menu(item_id: int, name: str):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            menu_item['name'] = name
            read_file.close()

            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            
            return {"Response": "Menu data updated"}

# Add Menu
@app.post('/menu')
async def add_menu(name: str):
    id = 1
    if (len(data['menu']) >= 1):
        id = data['menu'][len(data['menu']) - 1]['id'] + 1
    
    new_menu = {'id': id, "name": name}
    data['menu'].append(new_menu)
    read_file.close()

    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
        
    return (new_menu)

    raise HTTPException(
		status_code=500, detail=f'Internal Server Error'
	)

# Delete Menu
@app.delete('/menu/{item_id}')
async def delete_menu(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()

            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            
            return {"Response": "Menu data deleted"}