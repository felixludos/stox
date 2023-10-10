import streamlit as st
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo


class Portfolio:
	def __init__(self, cards=None):
		self.cards = None
		if cards is not None:
			self.populate(cards)

	def populate(self, cards):
		for c in cards:
			c.weight = 100/len(cards)
			c.set_portfolio(self)
		self.cards = cards

	def update_weight(self, card, new_value):
		other = [c for c in self.cards if c != card and not c.locked]
		delta = card.weight - new_value
		fixed = sum(c.weight for c in self.cards if c.locked)
		current = sum(c.weight for c in other)

		if not len(other):
			st.error(f'Cannot update weight of {card.name} because it is the only unlocked card.')

		for c in other:
			new = c.weight + delta * (1/len(other) if current == 0 else c.weight / current)
			c.weight = min(max(0., new), 100.)

		card.weight = 100 - (fixed + sum(c.weight for c in other))

	def display(self):
		with st.sidebar:
			for card in self.cards:
				card.display()


class Card:
	def __init__(self, name: str, weight=1., portfolio=None):
		self.p = portfolio
		self.name = name
		self.weight = weight
		self.locked = False

	def set_portfolio(self, portfolio):
		self.p = portfolio


	def toggle_lock(self):
		self.locked = not self.locked


	def update_weight(self):
		self.p.update_weight(self, float(st.session_state[f'weight_{self.name}']))
		return self.weight


	def display(self):
		with st.expander(self.name):
			st.write('Company profile and details')

		col1, col2 = st.columns([4, 1])
		with col1:
			st.slider('Weight', 0., 10.,
									self.weight,
									key=f'weight_{self.name}',
									disabled=self.locked, on_change=self.update_weight, label_visibility='collapsed')
			# st.markdown(f'<p style="color:#333;">{self.name}</p>', unsafe_allow_html=True)
		with col2:
			st.button('🔓' if self.locked else '🔒', key=f'lock_{self.name}', on_click=self.toggle_lock)












