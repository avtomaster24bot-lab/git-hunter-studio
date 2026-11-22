from PIL import ImageFont
P="/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"
def F(size,w="Black"):
    f=ImageFont.truetype(P,size)
    try: f.set_variation_by_name(w)
    except Exception:
        try: f.set_variation_by_axes([32,{"Black":900,"ExtraBold":800,"Bold":700,"SemiBold":600,"Regular":400}[w]])
        except Exception: pass
    return f
