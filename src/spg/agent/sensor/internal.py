##################
# Internal Sensors
##################


class InternalSensor(Sensor, ABC):

    """
    Base Class for Internal Sensors.
    """

    def _default_value(self):
        return np.zeros(self.shape)

    def _apply_noise(self):
        if self._noise_type == "gaussian":
            additive_noise = np.random.normal(
                self._noise_mean, self._noise_scale, size=self.shape
            )

        else:
            raise ValueError

        self.sensor_values += additive_noise

    def draw(self, width: int, height: int):
        img = Image.new("RGB", (width, height), (255, 255, 255))
        drawer_image = ImageDraw.Draw(img)

        if self.sensor_values is not None:
            fnt = ImageFont.truetype(
                "Pillow/Tests/fonts/FreeMono.ttf", int(height * 1 / 2)
            )
            values_str = ", ".join(["%.2f" % e for e in self.sensor_values])
            w_text, h_text = fnt.getsize(text=values_str)
            pos_text = ((width - w_text) / 2, (height - h_text) / 2)
            drawer_image.text(pos_text, values_str, font=fnt, fill=(0, 0, 0))

        return np.asarray(img) / 255.0
